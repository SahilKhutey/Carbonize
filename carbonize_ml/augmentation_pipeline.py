"""
Production Data Augmentation Pipeline
Fixes Bottleneck B20: Dataset quality
"""

import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass, asdict
from tqdm import tqdm
import random
import yaml


@dataclass
class AugmentationConfig:
    """Augmentation policy configuration."""
    
    # ─── Photometric ────────────────────────────────────────────────
    brightness_range: Tuple[float, float] = (-0.2, 0.2)
    contrast_range: Tuple[float, float] = (0.8, 1.2)
    gamma_range: Tuple[float, float] = (80, 120)
    hue_shift: int = 10
    saturation_range: Tuple[float, float] = (0.8, 1.2)
    value_range: Tuple[float, float] = (0.8, 1.2)
    
    # ─── Noise ──────────────────────────────────────────────────────
    gaussian_noise_var: Tuple[int, int] = (10, 50)
    iso_noise_prob: float = 0.3
    motion_blur_prob: float = 0.2
    gaussian_blur_prob: float = 0.3
    
    # ─── Geometric ──────────────────────────────────────────────────
    rotation_deg: int = 15
    scale_range: Tuple[float, float] = (0.8, 1.2)
    translate_range: Tuple[float, float] = (-0.1, 0.1)
    shear_deg: int = 5
    perspective_prob: float = 0.2
    horizontal_flip_prob: float = 0.5
    vertical_flip_prob: float = 0.0
    
    # ─── Weather / domain randomization ─────────────────────────────
    fog_prob: float = 0.3
    rain_prob: float = 0.2
    snow_prob: float = 0.1
    sun_flare_prob: float = 0.15
    shadow_prob: float = 0.4
    
    # ─── CO2-specific ───────────────────────────────────────────────
    haze_prob: float = 0.3         # Atmospheric haze
    gas_cloud_prob: float = 0.2    # Synthetic CO2 cloud overlay
    
    # ─── Output ─────────────────────────────────────────────────────
    augmentations_per_image: int = 5
    preserve_original: bool = True


class CarbonCaptureAugmentationPipeline:
    """Multi-modal augmentation pipeline with CO2-specific transforms."""
    
    def __init__(self, config: Optional[AugmentationConfig] = None):
        self.config = config or AugmentationConfig()
        self.transform = self._build_transform()
    
    def _build_transform(self) -> A.Compose:
        """Build albumentations pipeline."""
        c = self.config
        return A.Compose([
            # ─── Photometric ────────────────────────────────────────
            A.RandomBrightnessContrast(
                brightness_limit=c.brightness_range,
                contrast_limit=c.contrast_range,
                p=0.7
            ),
            A.HueSaturationValue(
                hue_shift_limit=c.hue_shift,
                sat_shift_limit=c.saturation_range[1] - 1.0,
                val_shift_limit=c.value_range[1] - 1.0,
                p=0.5
            ),
            A.RandomGamma(gamma_limit=(c.gamma_range[0], c.gamma_range[1]), p=0.5),
            A.CLAHE(p=0.3),
            
            # ─── Noise ──────────────────────────────────────────────
            A.GaussNoise(
                var_limit=c.gaussian_noise_var,
                p=0.5
            ),
            A.ISONoise(p=c.iso_noise_prob),
            A.MotionBlur(blur_limit=7, p=c.motion_blur_prob),
            A.GaussianBlur(blur_limit=(3, 7), p=c.gaussian_blur_prob),
            
            # ─── Geometric ──────────────────────────────────────────
            A.Affine(
                rotate=c.rotation_deg,
                scale=c.scale_range,
                translate_percent=c.translate_range,
                shear=c.shear_deg,
                p=0.6
            ),
            A.Perspective(scale=(0.05, 0.1), p=c.perspective_prob),
            A.HorizontalFlip(p=c.horizontal_flip_prob),
            A.VerticalFlip(p=c.vertical_flip_prob),
            
            # ─── Weather ────────────────────────────────────────────
            A.RandomFog(fog_coef_lower=0.1, fog_coef_upper=0.5, p=c.fog_prob),
            A.RandomRain(slant_lower=-10, slant_upper=10, drop_length=20, 
                         drop_width=1, drop_color=(200, 200, 200), 
                         blur_value=3, brightness_coefficient=0.8, p=c.rain_prob),
            A.RandomSnow(snow_point_lower=0.1, snow_point_upper=0.3, 
                         brightness_coeff=1.5, p=c.snow_prob),
            A.RandomSunFlare(flare_roi=(0, 0, 1, 0.5), 
                             angle_lower=0, angle_upper=1,
                             num_flare_circles_lower=2, num_flare_circles_upper=5,
                             src_radius=200, src_color=(255, 255, 255), p=c.sun_flare_prob),
            A.RandomShadow(p=c.shadow_prob),
            
            # ─── CO2-specific ───────────────────────────────────────
            A.RandomFog(fog_coef_lower=0.3, fog_coef_upper=0.8, p=c.haze_prob),
        ], bbox_params=A.BboxParams(
            format='yolo',
            label_fields=['class_labels'],
            min_visibility=0.3
        ))
    
    def augment_dataset(self, images_dir: str, labels_dir: str,
                        output_dir: str, class_names: List[str]) -> Dict:
        """Augment entire dataset in place."""
        images_path = Path(images_dir)
        labels_path = Path(labels_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        stats = {
            'original_count': 0,
            'augmented_count': 0,
            'skipped_corrupt': 0,
            'files': []
        }
        
        # ─── Load CO2-realistic colors ───────────────────────────────
        co2_colors = [
            (180, 200, 220),  # Haze blue
            (160, 180, 200),  # Industrial haze
            (200, 210, 230),  # Light CO2
        ]
        
        image_files = list(images_path.glob('*.jpg')) + list(images_path.glob('*.png'))
        
        for img_path in tqdm(image_files, desc='Augmenting'):
            label_path = labels_path / (img_path.stem + '.txt')
            
            image = cv2.imread(str(img_path))
            if image is None:
                stats['skipped_corrupt'] += 1
                continue
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            bboxes, class_labels = self._load_yolo_labels(label_path, class_names)
            
            # ─── Generate N augmentations ─────────────────────────────
            for i in range(self.config.augmentations_per_image):
                try:
                    augmented = self.transform(
                        image=image,
                        bboxes=bboxes,
                        class_labels=class_labels
                    )
                    
                    aug_img = augmented['image']
                    aug_bboxes = augmented['bboxes']
                    aug_labels = augmented['class_labels']
                    
                    if len(aug_bboxes) == 0:
                        continue
                    
                    # ─── CO2 cloud overlay ───────────────────────────
                    if random.random() < self.config.gas_cloud_prob:
                        aug_img = self._add_gas_cloud(aug_img, co2_colors)
                    
                    # ─── Save ─────────────────────────────────────────
                    aug_img_bgr = cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR)
                    out_name = f"{img_path.stem}_aug{i:02d}"
                    cv2.imwrite(str(output_path / f"{out_name}.jpg"), aug_img_bgr)
                    
                    self._save_yolo_labels(
                        output_path / f"{out_name}.txt",
                        aug_bboxes, aug_labels
                    )
                    
                    stats['augmented_count'] += 1
                    stats['files'].append(out_name)
                    
                except Exception as e:
                    continue
            
            if self.config.preserve_original:
                # Copy original
                cv2.imwrite(str(output_path / img_path.name), 
                            cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                if label_path.exists():
                    (output_path / label_path.name).write_text(label_path.read_text())
            
            stats['original_count'] += 1
        
        return stats
    
    def _load_yolo_labels(self, label_path: Path, 
                          class_names: List[str]) -> Tuple[List, List]:
        """Load YOLO format labels."""
        bboxes = []
        class_labels = []
        if not label_path.exists():
            return bboxes, class_labels
        for line in label_path.read_text().strip().split('\n'):
            if not line:
                continue
            parts = line.split()
            cls_id = int(parts[0])
            x_c, y_c, w, h = map(float, parts[1:5])
            bboxes.append([x_c, y_c, w, h])
            class_labels.append(class_names[cls_id] if cls_id < len(class_names) else 'object')
        return bboxes, class_labels
    
    def _save_yolo_labels(self, path: Path, bboxes: List, labels: List):
        """Save YOLO format labels."""
        with open(path, 'w') as f:
            for bbox, label in zip(bboxes, labels):
                cls_id = 0
                f.write(f"{cls_id} {bbox[0]:.6f} {bbox[1]:.6f} {bbox[2]:.6f} {bbox[3]:.6f}\n")
    
    def _add_gas_cloud(self, image: np.ndarray, colors: List[Tuple]) -> np.ndarray:
        """Overlay synthetic CO2 gas cloud."""
        overlay = image.copy()
        h, w = image.shape[:2]
        
        num_clouds = random.randint(1, 3)
        for _ in range(num_clouds):
            centroid = (random.randint(0, w), random.randint(0, h))
            radius = random.randint(50, 200)
            color = random.choice(colors)
            
            mask = np.zeros((h, w), dtype=np.float32)
            cv2.circle(mask, centroid, radius, 1.0, -1)
            mask = cv2.GaussianBlur(mask, (51, 51), 30)
            mask = (mask / max(mask.max(), 1e-5)) * 0.3
            
            for c in range(3):
                overlay[:, :, c] = (overlay[:, :, c] * (1 - mask) + 
                                     color[c] * mask).astype(np.uint8)
        
        return overlay


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Augment CO2 detection dataset')
    parser.add_argument('--images', required=True, help='Images directory')
    parser.add_argument('--labels', required=True, help='Labels directory (YOLO format)')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--dataset-yaml', required=True, help='dataset.yaml path')
    parser.add_argument('--per-image', type=int, default=5, help='Augmentations per image')
    args = parser.parse_args()
    
    with open(args.dataset_yaml) as f:
        cfg = yaml.safe_load(f)
    class_names = cfg['names']
    
    config = AugmentationConfig(augmentations_per_image=args.per_image)
    pipeline = CarbonCaptureAugmentationPipeline(config)
    stats = pipeline.augment_dataset(args.images, args.labels, args.output, class_names)
    
    print(f"\n✓ Augmented: {stats['augmented_count']} new images")
    print(f"  Original: {stats['original_count']} preserved")
    print(f"  Skipped: {stats['skipped_corrupt']} corrupt")


if __name__ == '__main__':
    main()

"""
Production YOLO Export Pipeline
Fixes Bottleneck B16: Edge deployment optimization
"""

import os
import sys
import time
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from ultralytics import YOLO
import torch
import numpy as np


@dataclass
class ExportSpec:
    """Per-format export parameters."""
    name: str
    format: str
    imgsz: int = 640
    half: bool = True
    int8: bool = False
    device: str = 'cuda'
    extra: Dict = None


@dataclass
class BenchmarkResult:
    """Benchmark metrics for one format."""
    format: str
    model_size_mb: float
    load_time_ms: float
    warmup_ms: float
    mean_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    fps: float
    gpu_memory_mb: float
    mAP50: float
    mAP50_95: float


class YOLOExportPipeline:
    """Multi-format export with automated benchmarking."""
    
    EXPORT_SPECS = [
        ExportSpec('onnx_fp16', 'onnx', half=True),
        ExportSpec('onnx_int8', 'onnx', half=False, int8=True),
        ExportSpec('engine_fp16', 'engine', half=True),
        ExportSpec('engine_int8', 'engine', half=True, int8=True),
        ExportSpec('openvino_fp16', 'openvino', half=True),
        ExportSpec('tflite_fp16', 'tflite', half=True),
        ExportSpec('coreml_fp16', 'coreml', half=True),
        ExportSpec('edgetpu', 'edgetpu', half=True),
    ]
    
    def __init__(self, weights_path: str, data_yaml: str = 'data/dataset.yaml',
                 output_dir: str = 'exports/', benchmark_iters: int = 200):
        self.weights = Path(weights_path)
        self.data_yaml = data_yaml
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.benchmark_iters = benchmark_iters
        
        if not self.weights.exists():
            raise FileNotFoundError(f"Weights not found: {self.weights}")
        
        self.model = YOLO(str(self.weights))
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def export_all(self) -> List[Path]:
        """Export to all supported formats."""
        exported = []
        for spec in self.EXPORT_SPECS:
            try:
                path = self._export_one(spec)
                if path:
                    exported.append(path)
            except Exception as e:
                print(f"✗ {spec.name} failed: {e}")
        return exported
    
    def _export_one(self, spec: ExportSpec) -> Optional[Path]:
        """Export to a single format with calibration if needed."""
        print(f"→ Exporting {spec.name}...")
        
        # ─── Prepare export kwargs ─────────────────────────────────
        kwargs = {
            'format': spec.format,
            'imgsz': spec.imgsz,
            'half': spec.half,
            'device': spec.device,
            'optimize': True,
            'simplify': True if spec.format == 'onnx' else False,
        }
        
        if spec.int8:
            kwargs['int8'] = True
            kwargs['data'] = self.data_yaml
            kwargs['calibration_data'] = None  # Auto-discover
        
        try:
            exported_path = self.model.export(**kwargs)
            print(f"✓ {spec.name}: {exported_path}")
            return Path(exported_path)
        except Exception as e:
            print(f"✗ {spec.name} error: {e}")
            return None
    
    def benchmark_all(self, exported_paths: List[Path]) -> List[BenchmarkResult]:
        """Benchmark all exported formats."""
        results = []
        
        for path in exported_paths:
            try:
                result = self._benchmark_one(path)
                results.append(result)
                self._print_result(result)
            except Exception as e:
                print(f"✗ Benchmark failed for {path}: {e}")
        
        return results
    
    def _benchmark_one(self, model_path: Path) -> BenchmarkResult:
        """Run benchmark on a single model."""
        print(f"→ Benchmarking {model_path.name}...")
        
        # ─── Load model ─────────────────────────────────────────────
        t0 = time.perf_counter()
        model = YOLO(str(model_path))
        load_time = (time.perf_counter() - t0) * 1000
        
        # ─── Prepare dummy input ────────────────────────────────────
        dummy = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
        
        # ─── Warmup ─────────────────────────────────────────────────
        warmup_times = []
        for _ in range(10):
            t = time.perf_counter()
            _ = model.predict(dummy, verbose=False)
            warmup_times.append((time.perf_counter() - t) * 1000)
        warmup_ms = np.mean(warmup_times)
        
        # ─── Measured runs ──────────────────────────────────────────
        latencies = []
        for _ in range(self.benchmark_iters):
            t = time.perf_counter()
            _ = model.predict(dummy, verbose=False)
            latencies.append((time.perf_counter() - t) * 1000)
        
        latencies = np.array(latencies)
        
        # ─── GPU memory ─────────────────────────────────────────────
        gpu_mem_mb = 0.0
        if torch.cuda.is_available():
            gpu_mem_mb = torch.cuda.max_memory_allocated() / 1024 / 1024
            torch.cuda.reset_peak_memory_stats()
        
        # ─── Validation (mAP) ───────────────────────────────────────
        try:
            metrics = model.val(data=self.data_yaml, verbose=False)
            mAP50 = float(metrics.box.map50)
            mAP50_95 = float(metrics.box.map)
        except Exception:
            mAP50 = mAP50_95 = 0.0
        
        return BenchmarkResult(
            format=model_path.suffix.lstrip('.'),
            model_size_mb=model_path.stat().st_size / 1024 / 1024,
            load_time_ms=load_time,
            warmup_ms=warmup_ms,
            mean_latency_ms=float(np.mean(latencies)),
            p50_latency_ms=float(np.percentile(latencies, 50)),
            p95_latency_ms=float(np.percentile(latencies, 95)),
            p99_latency_ms=float(np.percentile(latencies, 99)),
            fps=1000.0 / float(np.mean(latencies)),
            gpu_memory_mb=gpu_mem_mb,
            mAP50=mAP50,
            mAP50_95=mAP50_95
        )
    
    def _print_result(self, r: BenchmarkResult) -> None:
        """Pretty-print benchmark result."""
        print(f"\n{'='*60}")
        print(f"  Format: {r.format}")
        print(f"  Model size: {r.model_size_mb:.1f} MB")
        print(f"  Mean latency: {r.mean_latency_ms:.1f} ms ({r.fps:.1f} FPS)")
        print(f"  P50/P95/P99: {r.p50_latency_ms:.1f} / {r.p95_latency_ms:.1f} / {r.p99_latency_ms:.1f} ms")
        print(f"  GPU memory: {r.gpu_memory_mb:.0f} MB")
        print(f"  mAP@50: {r.mAP50:.3f} | mAP@50-95: {r.mAP50_95:.3f}")
        print(f"{'='*60}\n")
    
    def save_report(self, results: List[BenchmarkResult], path: str = 'benchmark_report.json'):
        """Save benchmark report to JSON + Markdown."""
        # ─── JSON ───────────────────────────────────────────────────
        with open(path, 'w') as f:
            json.dump([asdict(r) for r in results], f, indent=2)
        
        # ─── Markdown table ─────────────────────────────────────────
        md_path = path.replace('.json', '.md')
        with open(md_path, 'w') as f:
            f.write("# YOLO Export Benchmark Report\n\n")
            f.write("| Format | Size (MB) | Mean (ms) | p95 (ms) | p99 (ms) | FPS | GPU (MB) | mAP50 | mAP50-95 |\n")
            f.write("|--------|-----------|-----------|----------|----------|-----|----------|-------|----------|\n")
            for r in sorted(results, key=lambda x: x.mean_latency_ms):
                f.write(
                    f"| {r.format} | {r.model_size_mb:.1f} | {r.mean_latency_ms:.1f} | "
                    f"{r.p95_latency_ms:.1f} | {r.p99_latency_ms:.1f} | {r.fps:.1f} | "
                    f"{r.gpu_memory_mb:.0f} | {r.mAP50:.3f} | {r.mAP50_95:.3f} |\n"
                )
            
            # ─── Best recommendation ─────────────────────────────────
            best_latency = min(results, key=lambda x: x.mean_latency_ms)
            best_size = min(results, key=lambda x: x.model_size_mb)
            best_acc = max(results, key=lambda x: x.mAP50_95)
            
            f.write(f"\n## Recommendations\n\n")
            f.write(f"- **Lowest latency**: `{best_latency.format}` ({best_latency.mean_latency_ms:.1f}ms)\n")
            f.write(f"- **Smallest size**: `{best_size.format}` ({best_size.model_size_mb:.1f}MB)\n")
            f.write(f"- **Best accuracy**: `{best_acc.format}` (mAP50-95={best_acc.mAP50_95:.3f})\n")
        
        print(f"✓ Report saved: {path} + {md_path}")


def main():
    parser = argparse.ArgumentParser(description='YOLO export + benchmark pipeline')
    parser.add_argument('--weights', required=True, help='Path to .pt weights')
    parser.add_argument('--data', default='data/dataset.yaml', help='Dataset YAML')
    parser.add_argument('--output', default='exports/', help='Output directory')
    parser.add_argument('--iters', type=int, default=200, help='Benchmark iterations')
    parser.add_argument('--formats', nargs='+', default=None, help='Specific formats to export')
    args = parser.parse_args()
    
    pipeline = YOLOExportPipeline(
        weights_path=args.weights,
        data_yaml=args.data,
        output_dir=args.output,
        benchmark_iters=args.iters
    )
    
    if args.formats:
        pipeline.EXPORT_SPECS = [s for s in pipeline.EXPORT_SPECS if s.name in args.formats]
    
    exported = pipeline.export_all()
    results = pipeline.benchmark_all(exported)
    pipeline.save_report(results)


if __name__ == '__main__':
    main()

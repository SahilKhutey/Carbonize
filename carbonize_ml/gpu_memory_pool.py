"""
GPU Memory Pool for Inference
Fixes Bottleneck B26: GPU memory fragmentation
"""

import torch
import numpy as np
import cv2
import threading
from typing import Tuple, Optional, Dict
from dataclasses import dataclass
from collections import defaultdict
from contextlib import contextmanager
import time
import logging


logger = logging.getLogger('gpu-memory-pool')


@dataclass(frozen=True)
class TensorPoolKey:
    """Key for pooling tensors."""
    shape: Tuple[int, ...]
    dtype: torch.dtype
    device: str


class GPUMemoryPool:
    """
    Pre-allocated GPU tensor pool to eliminate fragmentation.
    
    Strategy:
        - Pre-allocate tensors of common shapes at startup
        - Reuse via reference counting
        - Fall back to allocation if pool miss
    """
    
    def __init__(self, device: str = 'cuda', 
                 pool_size_gb: float = 4.0,
                 max_pool_per_shape: int = 8):
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.max_pool_per_shape = max_pool_per_shape
        self.pool_size_bytes = int(pool_size_gb * 1024**3)
        
        self._pool: Dict[TensorPoolKey, list] = defaultdict(list)
        self._in_use: Dict[int, TensorPoolKey] = {}  # tensor_id -> key
        self._lock = threading.Lock()
        
        self._hits = 0
        self._misses = 0
        self._current_allocated = 0
        
        self._preallocate_common()
    
    def _preallocate_common(self):
        """Pre-allocate tensors for common inference shapes."""
        common_shapes = [
            (1, 3, 640, 640),     # Standard YOLO input
            (1, 3, 1280, 1280),   # High-res YOLO
            (1, 3, 320, 320),     # Low-res YOLO
            (4, 3, 640, 640),     # Batch 4
            (8, 3, 640, 640),     # Batch 8
            (1, 256, 80, 80),     # Feature maps
            (1, 512, 40, 40),
            (1, 1024, 20, 20),
        ]
        
        for shape in common_shapes:
            key = TensorPoolKey(shape, torch.float32, self.device)
            for _ in range(2):
                try:
                    tensor = torch.empty(shape, dtype=torch.float32, device=self.device)
                    self._pool[key].append(tensor)
                    self._current_allocated += tensor.element_size() * tensor.nelement()
                except Exception:
                    logger.warning(f'Pre-allocation skipped for shape {shape}')
                    break
        
        logger.info(f'Pre-allocated {len(self._pool)} shapes, '
                   f'{self._current_allocated / 1024**2:.0f}MB')
    
    def acquire(self, shape: Tuple[int, ...], 
                dtype: torch.dtype = torch.float32) -> Optional[torch.Tensor]:
        """Acquire tensor from pool."""
        key = TensorPoolKey(shape, dtype, self.device)
        
        with self._lock:
            if self._pool[key]:
                tensor = self._pool[key].pop()
                self._in_use[id(tensor)] = key
                self._hits += 1
                return tensor
            
            self._misses += 1
            
            tensor_size = int(torch.tensor(shape).prod().item() * 
                            torch.tensor([], dtype=dtype).element_size())
            
            if self._current_allocated + tensor_size < self.pool_size_bytes:
                try:
                    tensor = torch.empty(shape, dtype=dtype, device=self.device)
                    self._in_use[id(tensor)] = key
                    self._current_allocated += tensor_size
                    return tensor
                except Exception:
                    logger.error('GPU allocation failed during acquire')
                    return None
            
            self._evict_lru()
            return self.acquire(shape, dtype)
    
    def release(self, tensor: torch.Tensor):
        """Release tensor back to pool."""
        if tensor is None:
            return
        
        tensor_id = id(tensor)
        with self._lock:
            if tensor_id not in self._in_use:
                return
            
            key = self._in_use.pop(tensor_id)
            
            if len(self._pool[key]) < self.max_pool_per_shape:
                self._pool[key].append(tensor)
            else:
                self._current_allocated -= (
                    tensor.element_size() * tensor.nelement()
                )
    
    def _evict_lru(self):
        """Evict least-recently-used pool entry."""
        for key, tensors in self._pool.items():
            if tensors:
                tensor = tensors.pop(0)
                self._current_allocated -= (
                    tensor.element_size() * tensor.nelement()
                )
                return
    
    @contextmanager
    def acquire_context(self, shape: Tuple[int, ...], 
                        dtype: torch.dtype = torch.float32):
        """Context manager for auto-release."""
        tensor = self.acquire(shape, dtype)
        try:
            yield tensor
        finally:
            if tensor is not None:
                self.release(tensor)
    
    def get_stats(self) -> Dict:
        """Get pool statistics."""
        with self._lock:
            total_tensors = (sum(len(t) for t in self._pool.values()) + 
                           len(self._in_use))
            return {
                'pool_hits': self._hits,
                'pool_misses': self._misses,
                'hit_rate': self._hits / max(self._hits + self._misses, 1),
                'in_use_tensors': len(self._in_use),
                'pooled_tensors': total_tensors,
                'current_allocated_mb': self._current_allocated / 1024**2,
                'pool_size_gb': self.pool_size_bytes / 1024**3,
                'shapes_cached': len(self._pool)
            }
    
    def clear(self):
        """Clear all pooled tensors."""
        with self._lock:
            self._pool.clear()
            self._in_use.clear()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# Global instance
pool = GPUMemoryPool(device='cuda' if torch.cuda.is_available() else 'cpu', pool_size_gb=4.0)

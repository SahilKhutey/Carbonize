"""
Idempotency utilities for Celery tasks.

A task is idempotent if running it multiple times produces the same
result (or has the same effect) as running it once.
"""

import functools
import hashlib
import json
from typing import Any, Callable
from datetime import datetime, timezone

from cbms_shared.logging import get_logger


logger = get_logger(__name__)


def idempotent_task(
    func: Callable = None,
    *,
    key_fields: list[str] = None,
    dedup_window_seconds: int = 3600,
):
    """
    Decorator that makes a Celery task idempotent.
    
    If the same task_id (or same input) is submitted within
    dedup_window_seconds, the duplicate is ignored.
    
    This is an in-memory dedup (per worker). For distributed dedup,
    use Redis-based dedup.
    """
    def decorator(func: Callable) -> Callable:
        # In-memory dedup cache: (task_name, input_hash) -> (result, timestamp)
        _cache: dict[tuple, tuple[Any, datetime]] = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Compute input hash
            input_data = {"args": args, "kwargs": kwargs}
            if key_fields:
                # Only hash specified fields
                input_data = {
                    k: v for k, v in input_data["kwargs"].items() if k in key_fields
                }
            input_str = json.dumps(input_data, sort_keys=True, default=str)
            input_hash = hashlib.sha256(input_str.encode()).hexdigest()[:16]
            
            cache_key = (func.__name__, input_hash)
            
            # Check cache
            if cache_key in _cache:
                cached_result, cached_time = _cache[cache_key]
                age = (datetime.now(timezone.utc) - cached_time).total_seconds()
                if age < dedup_window_seconds:
                    logger.info(
                        "task_dedup_hit",
                        task=func.__name__,
                        input_hash=input_hash,
                        age_seconds=age,
                    )
                    return cached_result
                else:
                    # Cache expired
                    del _cache[cache_key]
            
            # Execute task
            result = func(*args, **kwargs)
            
            # Cache result
            _cache[cache_key] = (result, datetime.now(timezone.utc))
            
            # Limit cache size (prevent memory leak)
            if len(_cache) > 10000:
                # Remove oldest entries
                sorted_keys = sorted(_cache, key=lambda k: _cache[k][1])
                for k in sorted_keys[:1000]:
                    del _cache[k]
            
            return result
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


def compute_task_idempotency_key(*args, **kwargs) -> str:
    """Compute a deterministic key from task inputs."""
    data = {"args": args, "kwargs": kwargs}
    serialized = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()[:32]


def run_async_task(coro) -> Any:
    """
    Execute an async coroutine synchronously.
    
    Safe to use even if an event loop is already running in the current thread
    (e.g., during pytest execution).
    """
    import asyncio
    import concurrent.futures
    
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
        
    if loop and loop.is_running():
        # Run in a separate thread to avoid blocking the running event loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)


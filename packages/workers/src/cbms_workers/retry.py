"""
Retry policies for Celery tasks.

Implements exponential backoff with jitter to prevent thundering herd.
"""

import time
import random
import functools
from typing import Callable

from cbms_shared.logging import get_logger


logger = get_logger(__name__)


# Exception types that should be retried
RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    IOError,
    OSError,
)


def report_retry_policy(
    max_attempts: int = 3,
    initial_delay_s: float = 2.0,
    max_delay_s: float = 60.0,
):
    """
    Create a retry decorator for report generation tasks.
    
    Strategy:
    - Exponential backoff: 2s, 4s, 8s, 16s, ...
    - With jitter to prevent thundering herd
    - Max 3 attempts (then mark as FAILED)
    
    Retryable: network errors, timeouts, transient S3/DB issues
    NOT retryable: validation errors, programming bugs
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay_s
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except RETRYABLE_EXCEPTIONS as e:
                    if attempt == max_attempts:
                        logger.error(
                            "task_retry_exhausted",
                            function=func.__name__,
                            attempt=attempt,
                            exception=str(e),
                        )
                        raise
                        
                    # Add jitter to delay (50% to 150%)
                    jitter = random.uniform(0.5, 1.5)
                    sleep_time = min(delay * jitter, max_delay_s)
                    
                    logger.info(
                        "task_retry",
                        function=func.__name__,
                        attempt=attempt,
                        delay=sleep_time,
                        exception=str(e),
                    )
                    
                    time.sleep(sleep_time)
                    delay *= 2
            return None
        return wrapper
    return decorator


# Celery-level retry configuration
def configure_celery_retry(task, autoretry_for: tuple = RETRYABLE_EXCEPTIONS):
    """
    Configure Celery-level retry for a task.
    """
    task.autoretry_for = autoretry_for
    task.retry_backoff = True  # Exponential
    task.retry_backoff_max = 60  # Max 60s
    task.retry_jitter = True  # Add jitter
    return task

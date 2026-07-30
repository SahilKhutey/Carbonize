"""
Async ROS 2 Service Client with Circuit Breaker
Fixes Bottleneck B21: Synchronous service calls blocking executor
"""

import rclpy
from rclpy.node import Node
from rclpy.task import Future
from rclpy.qos import QoSProfile
import asyncio
import time
from typing import TypeVar, Generic, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading


ServiceRequest = TypeVar('ServiceRequest')
ServiceResponse = TypeVar('ServiceResponse')


class CircuitState(Enum):
    CLOSED = "CLOSED"           # Normal operation
    OPEN = "OPEN"               # Failing fast
    HALF_OPEN = "HALF_OPEN"     # Testing


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_sec: float = 30.0
    half_open_max_calls: int = 1


class CircuitBreaker:
    """Circuit breaker for service calls."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self._lock = threading.Lock()
    
    def can_call(self) -> bool:
        with self._lock:
            if self.state == CircuitState.CLOSED:
                return True
            elif self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.config.timeout_sec:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True
                return False
            else:  # HALF_OPEN
                return self.success_count < self.config.half_open_max_calls
    
    def record_success(self):
        with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            else:
                self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN


class AsyncServiceClient(Generic[ServiceRequest, ServiceResponse]):
    """
    Async wrapper for ROS 2 service clients with circuit breaker.
    """
    
    def __init__(self, node: Node, service_type, service_name: str,
                 timeout_sec: float = 5.0, max_retries: int = 3,
                 breaker_config: Optional[CircuitBreakerConfig] = None):
        self.node = node
        self.client = node.create_client(service_type, service_name)
        self.timeout_sec = timeout_sec
        self.max_retries = max_retries
        self.breaker = CircuitBreaker(breaker_config or CircuitBreakerConfig())
        
        # ─── Metrics ───────────────────────────────────────────────
        self._call_count = 0
        self._success_count = 0
        self._failure_count = 0
        self._breaker_skip_count = 0
    
    async def wait_for_service(self, timeout_sec: float = 10.0) -> bool:
        """Async wait for service availability."""
        start = time.time()
        while time.time() - start < timeout_sec:
            if self.client.service_is_ready():
                return True
            await asyncio.sleep(0.1)
        return False
    
    async def call_async(self, request: ServiceRequest) -> Optional[ServiceResponse]:
        """
        Async service call with retry + circuit breaker.
        """
        if not self.breaker.can_call():
            self._breaker_skip_count += 1
            self.node.get_logger().warn(
                f'Circuit breaker OPEN, skipping call to {self.client.srv_name}'
            )
            return None
        
        self._call_count += 1
        
        for attempt in range(self.max_retries):
            try:
                if not self.client.wait_for_service(timeout_sec=1.0):
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(0.5 * (2 ** attempt))  # Exponential backoff
                        continue
                    self._failure_count += 1
                    self.breaker.record_failure()
                    return None
                
                # ─── Async call ─────────────────────────────────────
                future = self.client.call_async(request)
                response = await asyncio.wrap_future(future.future)
                
                self._success_count += 1
                self.breaker.record_success()
                return response
                
            except Exception as e:
                self.node.get_logger().warn(
                    f'Service call attempt {attempt+1}/{self.max_retries} failed: {e}'
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                else:
                    self._failure_count += 1
                    self.breaker.record_failure()
        
        return None
    
    def get_stats(self) -> dict:
        return {
            'call_count': self._call_count,
            'success_count': self._success_count,
            'failure_count': self._failure_count,
            'breaker_skip_count': self._breaker_skip_count,
            'success_rate': self._success_count / max(self._call_count, 1),
            'circuit_state': self.breaker.state.value
        }
    
    def destroy(self):
        self.node.destroy_client(self.client)


class MissionNode(Node):
    """Example using async service client."""
    
    def __init__(self):
        super().__init__('mission_node')
        
        from example_interfaces.srv import Trigger
        
        self.trigger_client = AsyncServiceClient(
            self,
            Trigger,
            '/robot/arm/deploy',
            timeout_sec=5.0,
            max_retries=3
        )
    
    async def deploy_capture_device(self):
        """Async deployment — doesn't block executor."""
        from example_interfaces.srv import Trigger
        
        if not await self.trigger_client.wait_for_service():
            self.get_logger().error('Service not available')
            return False
        
        request = Trigger.Request()
        response = await self.trigger_client.call_async(request)
        
        if response and response.success:
            self.get_logger().info('Capture device deployed')
            return True
        else:
            self.get_logger().warn('Deployment failed')
            return False

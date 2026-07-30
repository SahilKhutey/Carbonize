#!/usr/bin/env python3
"""
Clock Synchronization Bridge — Production-Grade
Fixes Bottleneck B15: Sim ↔ ROS clock desync
"""

import rclpy
from rclpy.node import Node
from rclpy.clock import ClockType, ROSClock
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import TimeReference
from builtin_interfaces.msg import Time
import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClockSample:
    """Single clock correlation observation."""
    sim_time_ns: int
    wall_time_ns: int
    drift_ns: int


class ClockBridge(Node):
    """
    Maintains high-fidelity correlation between Gazebo sim_time and ROS 2 time.
    
    Architecture:
        /clock (Gazebo) ──▶ Drift Estimator ──▶ /clock_offset (publisher)
                                          │
                                          ▼
                                  /time_reference (correction)
    """
    
    def __init__(self):
        super().__init__('clock_bridge')
        
        self.declare_parameter('max_drift_ms', 50.0)
        self.declare_parameter('sample_window', 100)
        self.declare_parameter('publish_correction_hz', 10.0)
        self.declare_parameter('auto_resync', True)
        self.declare_parameter('clock_topic', '/clock')
        self.declare_parameter('correction_topic', '/time_reference')
        
        self.max_drift_ns = int(self.get_parameter('max_drift_ms').value * 1e6)
        self.auto_resync = self.get_parameter('auto_resync').value
        
        # ─── QoS: Reliable for clock messages ───────────────────────
        clock_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            depth=10
        )
        
        # ─── Subscribers ─────────────────────────────────────────────
        self.clock_sub = self.create_subscription(
            Clock,
            self.get_parameter('clock_topic').value,
            self.clock_callback,
            clock_qos
        )
        
        # ─── Publishers ──────────────────────────────────────────────
        self.correction_pub = self.create_publisher(
            TimeReference,
            self.get_parameter('correction_topic').value,
            clock_qos
        )
        
        self.offset_pub = self.create_publisher(
            Clock,
            '/clock_offset',
            clock_qos
        )
        
        # ─── State ───────────────────────────────────────────────────
        self._samples: deque[ClockSample] = deque(maxlen=self.get_parameter('sample_window').value)
        self._lock = threading.Lock()
        self._last_sim_time_ns = 0
        self._last_wall_time_ns = 0
        self._current_drift_ns = 0
        
        # ─── Timer for periodic correction ───────────────────────────
        period = 1.0 / self.get_parameter('publish_correction_hz').value
        self.correction_timer = self.create_timer(period, self.publish_correction)
        
        self.get_logger().info('ClockBridge initialized ✓')
    
    def clock_callback(self, msg: Clock) -> None:
        """Receive /clock from Gazebo and compute drift."""
        sim_time_ns = msg.clock.sec * 1_000_000_000 + msg.clock.nanosec
        wall_time_ns = self.get_clock().now().nanoseconds
        
        with self._lock:
            # ─── Detect wraparound / backward jumps ──────────────────
            if sim_time_ns < self._last_sim_time_ns:
                self.get_logger().warn(
                    f'Sim time went backward: {self._last_sim_time_ns} → {sim_time_ns}'
                )
                self._last_sim_time_ns = sim_time_ns
                self._last_wall_time_ns = wall_time_ns
                return
            
            # ─── Compute instantaneous drift ─────────────────────────
            if self._last_sim_time_ns > 0:
                sim_delta = sim_time_ns - self._last_sim_time_ns
                wall_delta = wall_time_ns - self._last_wall_time_ns
                drift = sim_delta - wall_delta
                
                sample = ClockSample(sim_time_ns, wall_time_ns, drift)
                self._samples.append(sample)
                
                # ─── Compute median drift (robust to outliers) ───────
                if len(self._samples) >= 10:
                    drifts = sorted([s.drift_ns for s in self._samples])
                    median_drift = drifts[len(drifts) // 2]
                    self._current_drift_ns = median_drift
                    
                    # ─── Auto-resync if drift exceeds threshold ───────
                    if abs(median_drift) > self.max_drift_ns and self.auto_resync:
                        self.get_logger().warn(
                            f'Drift {median_drift / 1e6:.1f}ms exceeds threshold, triggering resync'
                        )
                        self._request_resync()
            
            self._last_sim_time_ns = sim_time_ns
            self._last_wall_time_ns = wall_time_ns
    
    def publish_correction(self) -> None:
        """Publish clock correction for downstream nodes."""
        with self._lock:
            if len(self._samples) < 10:
                return
            
            # ─── TimeReference message ────────────────────────────────
            tr = TimeReference()
            tr.header.stamp = self.get_clock().now().to_msg()
            tr.header.frame_id = 'clock_bridge'
            
            # Source: estimated sim epoch
            tr.source = f'sim_time + drift={self._current_drift_ns}ns'
            tr.time_ref = self._sim_to_msg(self._last_sim_time_ns + self._current_drift_ns)
            
            self.correction_pub.publish(tr)
            
            # ─── Offset clock for human inspection ────────────────────
            clk = Clock()
            clk.clock = self._sim_to_msg(self._current_drift_ns)
            self.offset_pub.publish(clk)
            
            # ─── Periodic health log ──────────────────────────────────
            if len(self._samples) % 100 == 0:
                drifts = sorted([s.drift_ns for s in self._samples])
                p99 = drifts[int(len(drifts) * 0.99)]
                self.get_logger().info(
                    f'Clock drift: median={self._current_drift_ns / 1e6:.2f}ms, '
                    f'p99={p99 / 1e6:.2f}ms, samples={len(self._samples)}'
                )
    
    def _request_resync(self) -> None:
        """Request Gazebo to resync its clock."""
        # Reset state to allow fresh correlation
        self._last_sim_time_ns = 0
        self._last_wall_time_ns = 0
        self._samples.clear()
    
    def _sim_to_msg(self, ns: int) -> Time:
        t = Time()
        t.sec = ns // 1_000_000_000
        t.nanosec = ns % 1_000_000_000
        return t


def main(args=None):
    rclpy.init(args=args)
    node = ClockBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

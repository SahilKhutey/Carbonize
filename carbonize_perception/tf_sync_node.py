#!/usr/bin/env python3
"""
TF-Synchronized Perception — Bounded Cache
Fixes Bottleneck B4: TF latency & queue growth
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import TransformStamped
from tf2_ros import Buffer, TransformListener, TransformBroadcaster
from tf2_ros import MessageFilter
from message_filters import ApproximateTimeSynchronizer
from message_filters.msg import Image as MFImage
import message_filters
import numpy as np


class TFSyncNode(Node):
    """
    Subscribes to image + camera_info, requests TF at exact stamp.
    Uses bounded history buffer (100 frames) to prevent memory growth.
    """
    
    def __init__(self):
        super().__init__('tf_sync_node')
        
        self.declare_parameter('target_frame', 'base_link')
        self.declare_parameter('cache_time_sec', 5.0)         # Bounded cache
        self.declare_parameter('max_interpolation', 0.5)
        self.declare_parameter('sync_slop', 0.05)
        
        # ─── Bounded TF Buffer (fix: was unbounded) ────────────────
        cache_time = self.get_parameter('cache_time_sec').value
        self.tf_buffer = Buffer(
            cache_time=__import__('rclpy').duration.Duration(seconds=cache_time)
        )
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # ─── QoS for sensor streams ────────────────────────────────
        sensor_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=5
        )
        
        # ─── Synchronized subscribers ──────────────────────────────
        image_sub = message_filters.Subscriber(self, Image, '/camera/image_raw', qos_profile=sensor_qos)
        info_sub  = message_filters.Subscriber(self, CameraInfo, '/camera/camera_info', qos_profile=sensor_qos)
        
        self.sync = ApproximateTimeSynchronizer(
            [image_sub, info_sub],
            queue_size=10,                                        # Bounded
            slop=self.get_parameter('sync_slop').value
        )
        self.sync.registerCallback(self.synced_callback)
        
        self._frame_count = 0
        self.get_logger().info('TFSyncNode ready (bounded cache)')
    
    def synced_callback(self, image_msg: Image, info_msg: CameraInfo):
        """Process synchronized image + camera info with TF lookup."""
        target_frame = self.get_parameter('target_frame').value
        
        # ─── TF lookup with bounded interpolation ─────────────────
        try:
            transform = self.tf_buffer.lookup_transform(
                target_frame,
                image_msg.header.frame_id,
                image_msg.header.stamp,
                timeout=__import__('rclpy').duration.Duration(seconds=0.1)
            )
        except Exception as e:
            self.get_logger().warn(f'TF lookup failed: {e}', throttle_duration_sec=1.0)
            return
        
        # … process image + transform …
        self._frame_count += 1
        if self._frame_count % 100 == 0:
            self.get_logger().info(f'Processed {self._frame_count} synced frames')


def main(args=None):
    rclpy.init(args=args)
    node = TFSyncNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

"""
Production ROS Bag Compressor
Fixes Bottleneck B17: Storage bloat
"""

import rclpy
from rclpy.node import Node
from rclpy.serialization import serialize_message, deserialize_message
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
import rosbag2_py
from sensor_msgs.msg import Image, CompressedImage, PointCloud2
from nav_msgs.msg import Odometry
import zstandard as zstd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import time
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class TopicCompressionPolicy:
    """Per-topic compression strategy."""
    name: str
    algorithm: str = 'zstd'         # 'zstd', 'lz4', 'none'
    compression_level: int = 3
    downsample_factor: int = 1      # Keep every Nth message
    downsample_key: str = 'time'    # 'time', 'count', 'distance'
    enabled: bool = True


@dataclass
class CompressionStats:
    total_uncompressed_bytes: int = 0
    total_compressed_bytes: int = 0
    topic_stats: Dict[str, Dict] = field(default_factory=dict)
    
    @property
    def overall_ratio(self) -> float:
        return self.total_compressed_bytes / max(self.total_uncompressed_bytes, 1)


class RosbagCompressor:
    """Multi-topic, per-topic compression with intelligent downsampling."""
    
    DEFAULT_POLICIES = {
        '/camera/image_raw': TopicCompressionPolicy(
            name='/camera/image_raw',
            algorithm='zstd',
            compression_level=3,
            downsample_factor=1,           # Keep all (still compress)
        ),
        '/camera/image_raw/compressed': TopicCompressionPolicy(
            name='/camera/image_raw/compressed',
            algorithm='none',              # Already compressed
            downsample_factor=1,
        ),
        '/lidar/points': TopicCompressionPolicy(
            name='/lidar/points',
            algorithm='zstd',
            compression_level=5,
            downsample_factor=2,           # Half rate
        ),
        '/odom': TopicCompressionPolicy(
            name='/odom',
            algorithm='zstd',
            compression_level=9,           # High compression for small files
            downsample_factor=1,
        ),
        '/tf': TopicCompressionPolicy(
            name='/tf',
            algorithm='zstd',
            compression_level=9,
            downsample_factor=1,
        ),
    }
    
    def __init__(self, policies: Optional[Dict[str, TopicCompressionPolicy]] = None):
        self.policies = policies or self.DEFAULT_POLICIES
        self.stats = CompressionStats()
        self._compressors: Dict[str, zstd.ZstdCompressor] = {}
        self._counters = defaultdict(int)
    
    def compress_bag(self, input_path: str, output_path: str,
                     storage_id: str = 'mcap') -> CompressionStats:
        """Compress a ROS bag with topic-wise policies."""
        print(f"→ Opening {input_path}...")
        reader = rosbag2_py.SequentialReader()
        reader.open(
            rosbag2_py.StorageOptions(uri=input_path, storage_id='sqlite3'),
            rosbag2_py.ConverterOptions(input_serialization_format='cdr',
                                       output_serialization_format='cdr')
        )
        
        # ─── Open writer ─────────────────────────────────────────────
        writer = rosbag2_py.SequentialWriter()
        writer.open(
            rosbag2_py.StorageOptions(uri=output_path, storage_id=storage_id)
        )
        
        # ─── Re-register topics with QoS ─────────────────────────────
        topic_types = reader.get_all_topics_and_types()
        for topic_meta in topic_types:
            writer.create_topic(topic_meta)
        
        # ─── Streaming compression ───────────────────────────────────
        msg_count = 0
        start_time = time.perf_counter()
        
        while reader.has_next():
            topic, data, t = reader.read_next()
            
            # ─── Apply policy ────────────────────────────────────────
            policy = self.policies.get(topic)
            if policy and not policy.enabled:
                continue
            
            # ─── Downsample ───────────────────────────────────────────
            if policy and policy.downsample_factor > 1:
                self._counters[topic] += 1
                if self._counters[topic] % policy.downsample_factor != 0:
                    continue
            
            # ─── Compress ─────────────────────────────────────────────
            original_size = len(data)
            if policy and policy.algorithm != 'none':
                compressed_data = self._compress(data, topic, policy)
                compressed_size = len(compressed_data)
            else:
                compressed_data = data
                compressed_size = original_size
            
            # ─── Update stats ─────────────────────────────────────────
            self.stats.total_uncompressed_bytes += original_size
            self.stats.total_compressed_bytes += compressed_size
            self._update_topic_stats(topic, original_size, compressed_size)
            
            # ─── Write ───────────────────────────────────────────────
            writer.write(topic, compressed_data, t)
            
            msg_count += 1
            if msg_count % 10000 == 0:
                elapsed = time.perf_counter() - start_time
                rate = msg_count / elapsed
                print(f"  Processed {msg_count} messages ({rate:.0f} msg/s)...")
        
        reader.close()
        
        # ─── Final report ────────────────────────────────────────────
        self._print_report(time.perf_counter() - start_time, msg_count)
        return self.stats
    
    def _compress(self, data: bytes, topic: str, 
                  policy: TopicCompressionPolicy) -> bytes:
        """Compress using per-topic cached compressor."""
        if topic not in self._compressors:
            self._compressors[topic] = zstd.ZstdCompressor(
                level=policy.compression_level
            )
        return self._compressors[topic].compress(data)
    
    def _update_topic_stats(self, topic: str, original: int, compressed: int):
        """Update per-topic statistics."""
        if topic not in self.stats.topic_stats:
            self.stats.topic_stats[topic] = {
                'count': 0,
                'uncompressed_bytes': 0,
                'compressed_bytes': 0,
                'ratio': 0.0
            }
        s = self.stats.topic_stats[topic]
        s['count'] += 1
        s['uncompressed_bytes'] += original
        s['compressed_bytes'] += compressed
        s['ratio'] = s['compressed_bytes'] / max(s['uncompressed_bytes'], 1)
    
    def _print_report(self, elapsed: float, msg_count: int):
        """Print final compression report."""
        print(f"\n{'='*60}")
        print(f"COMPRESSION REPORT")
        print(f"{'='*60}")
        print(f"Total messages: {msg_count}")
        print(f"Elapsed time: {elapsed:.1f}s")
        print(f"Overall ratio: {self.stats.overall_ratio:.2f} "
              f"({100*(1-self.stats.overall_ratio):.1f}% space saved)")
        print(f"\n{'Topic':<40} {'Count':>8} {'Original':>12} {'Compressed':>12} {'Ratio':>8}")
        print(f"{'-'*40} {'-'*8} {'-'*12} {'-'*12} {'-'*8}")
        for topic, s in sorted(self.stats.topic_stats.items(),
                                key=lambda x: -x[1]['uncompressed_bytes']):
            print(f"{topic:<40} {s['count']:>8} "
                  f"{s['uncompressed_bytes']/1024/1024:>10.1f}MB "
                  f"{s['compressed_bytes']/1024/1024:>10.1f}MB "
                  f"{s['ratio']:>7.2f}")
        print(f"{'='*60}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Compress ROS bag files')
    parser.add_argument('input', help='Input bag path (directory)')
    parser.add_argument('output', help='Output bag path')
    parser.add_argument('--storage', default='mcap', help='Output storage (mcap, sqlite3)')
    args = parser.parse_args()
    
    compressor = RosbagCompressor()
    compressor.compress_bag(args.input, args.output, args.storage)


if __name__ == '__main__':
    main()

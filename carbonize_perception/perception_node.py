#!/usr/bin/env python3
"""
Async YOLO Perception Node — Production-Grade
Author: Carbonize Engineering
Fixes Bottleneck B1: Synchronous Inference Blocking
"""

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray, Detection2D, ObjectHypothesisWithPose
from cv_bridge import CvBridge
from ultralytics import YOLO
import torch
import threading
from queue import Queue, Empty
from dataclasses import dataclass
from typing import Optional
import time

@dataclass
class InferenceResult:
    """Thread-safe inference result container."""
    detections: Detection2DArray
    inference_time_ms: float
    frame_id: str
    stamp: object
    timestamp_received: float


class AsyncPerceptionNode(Node):
    """
    Async YOLO-based perception node with decoupled inference.
    
    Architecture:
        Camera Callback (Reentrant) ──▶ Frame Queue ──▶ Inference Worker (Thread)
                                                        │
                                                        ▼
                                                  Result Queue ──▶ Publisher
    """
    
    def __init__(self):
        super().__init__('async_perception_node')
        
        # ─── Parameters ───────────────────────────────────────────────
        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('device', 'cuda' if torch.cuda.is_available() else 'cpu')
        self.declare_parameter('confidence_threshold', 0.5)
        self.declare_parameter('iou_threshold', 0.45)
        self.declare_parameter('frame_queue_size', 3)         # Bounded backpressure
        self.declare_parameter('result_queue_size', 5)
        self.declare_parameter('publish_rate_hz', 30.0)
        self.declare_parameter('drop_old_frames', True)       # Drop if inference behind
        self.declare_parameter('input_image_topic', '/camera/image_raw')
        self.declare_parameter('output_detection_topic', '/detections')
        
        model_path = self.get_parameter('model_path').value
        device = self.get_parameter('device').value
        self.conf_thresh = self.get_parameter('confidence_threshold').value
        self.iou_thresh = self.get_parameter('iou_threshold').value
        
        # ─── Model Loading ────────────────────────────────────────────
        self.get_logger().info(f'Loading YOLO model: {model_path} on {device}')
        self.model = YOLO(model_path)
        self.model.to(device)
        if device == 'cuda':
            self.model.half()  # FP16 for edge GPUs
        
        # ─── Queues with Backpressure ────────────────────────────────
        self.frame_queue: Queue = Queue(maxsize=self.get_parameter('frame_queue_size').value)
        self.result_queue: Queue = Queue(maxsize=self.get_parameter('result_queue_size').value)
        self.drop_old = self.get_parameter('drop_old_frames').value
        
        # ─── Callback Groups (separate execution contexts) ───────────
        self.camera_group = ReentrantCallbackGroup()
        self.publisher_group = MutuallyExclusiveCallbackGroup()
        
        # ─── QoS: BEST_EFFORT for high-rate image streams ────────────
        sensor_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        # ─── Subscribers / Publishers ─────────────────────────────────
        self.image_sub = self.create_subscription(
            Image,
            self.get_parameter('input_image_topic').value,
            self.image_callback,
            sensor_qos,
            callback_group=self.camera_group
        )
        
        self.detection_pub = self.create_publisher(
            Detection2DArray,
            self.get_parameter('output_detection_topic').value,
            10,
            callback_group=self.publisher_group
        )
        
        # ─── Worker Thread ────────────────────────────────────────────
        self._inference_thread = threading.Thread(
            target=self._inference_worker,
            name='yolo_inference_worker',
            daemon=True
        )
        self._inference_thread.start()
        
        # ─── Publisher Timer ─────────────────────────────────────────
        publish_period = 1.0 / self.get_parameter('publish_rate_hz').value
        self.publish_timer = self.create_timer(
            publish_period,
            self.publish_results,
            callback_group=self.publisher_group
        )
        
        # ─── Metrics ──────────────────────────────────────────────────
        self._frame_count = 0
        self._dropped_count = 0
        self._lock = threading.Lock()
        
        self.get_logger().info('AsyncPerceptionNode initialized ✓')
    
    # ─────────────────────────────────────────────────────────────────
    # CAMERA CALLBACK (non-blocking enqueue)
    # ─────────────────────────────────────────────────────────────────
    def image_callback(self, msg: Image) -> None:
        """Drop-in queue with optional drop-oldest policy."""
        try:
            if self.drop_old:
                # Try without blocking; if full, drop oldest
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()  # Discard oldest
                        with self._lock:
                            self._dropped_count += 1
                    except Empty:
                        pass
            self.frame_queue.put_nowait(msg)
        except Exception as e:
            self.get_logger().warn(f'Frame enqueue failed: {e}')
    
    # ─────────────────────────────────────────────────────────────────
    # INFERENCE WORKER (runs in dedicated thread)
    # ─────────────────────────────────────────────────────────────────
    def _inference_worker(self) -> None:
        """Continuous inference loop — never blocks the executor."""
        bridge = CvBridge()
        while rclpy.ok():
            try:
                msg = self.frame_queue.get(timeout=0.1)
            except Empty:
                continue
            
            try:
                t0 = time.perf_counter()
                frame = bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                
                # ─── YOLO Inference ──────────────────────────────────
                results = self.model.predict(
                    frame,
                    conf=self.conf_thresh,
                    iou=self.iou_thresh,
                    verbose=False,
                    device=self.get_parameter('device').value
                )
                
                det_array = self._convert_to_detection_array(results, msg.header)
                inference_ms = (time.perf_counter() - t0) * 1000.0
                
                result = InferenceResult(
                    detections=det_array,
                    inference_time_ms=inference_ms,
                    frame_id=msg.header.frame_id,
                    stamp=msg.header.stamp,
                    timestamp_received=time.time()
                )
                
                # Publish to result queue (non-blocking)
                if self.result_queue.full():
                    try:
                        self.result_queue.get_nowait()
                    except Empty:
                        pass
                self.result_queue.put_nowait(result)
                
                with self._lock:
                    self._frame_count += 1
                
            except Exception as e:
                self.get_logger().error(f'Inference worker error: {e}', throttle_duration_sec=2.0)
    
    # ─────────────────────────────────────────────────────────────────
    # PUBLISH CALLBACK (runs in executor)
    # ─────────────────────────────────────────────────────────────────
    def publish_results(self) -> None:
        """Pop latest result and publish to ROS topic."""
        try:
            result = self.result_queue.get_nowait()
            self.detection_pub.publish(result.detections)
            
            if self._frame_count % 100 == 0:
                with self._lock:
                    self.get_logger().info(
                        f'Processed {self._frame_count} frames | '
                        f'Dropped: {self._dropped_count} | '
                        f'Last inference: {result.inference_time_ms:.1f}ms'
                    )
        except Empty:
            pass
    
    # ─────────────────────────────────────────────────────────────────
    # YOLO → ROS Message Conversion
    # ─────────────────────────────────────────────────────────────────
    def _convert_to_detection_array(self, results, header) -> Detection2DArray:
        det_array = Detection2DArray()
        det_array.header = header
        
        for r in results:
            boxes = r.boxes
            if boxes is None:
                continue
            for box in boxes:
                det = Detection2D()
                det.header = header
                bbox = box.xyxy[0].cpu().numpy()
                det.bbox.center.position.x = float((bbox[0] + bbox[2]) / 2.0)
                det.bbox.center.position.y = float((bbox[1] + bbox[3]) / 2.0)
                det.bbox.size_x = float(bbox[2] - bbox[0])
                det.bbox.size_y = float(bbox[3] - bbox[1])
                
                hyp = ObjectHypothesisWithPose()
                cls_id = int(box.cls[0])
                hyp.hypothesis.class_id = self.model.names[cls_id]
                hyp.hypothesis.score = float(box.conf[0])
                det.results.append(hyp)
                det_array.detections.append(det)
        return det_array


def main(args=None):
    rclpy.init(args=args)
    node = AsyncPerceptionNode()
    
    # MultiThreadedExecutor enables true parallelism
    executor = MultiThreadedExecutor(num_threads=4)
    executor.add_node(node)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

"""
Behavior Tree for Autonomous Carbon Capture
Fixes Bottleneck B19: Tight coupling between perception and control
"""

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String, Bool, Float32
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Image
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable, Dict, List
from abc import ABC, abstractmethod
import time
import threading


class BTStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"


class BTNode(ABC):
    """Base behavior tree node."""
    
    def __init__(self, name: str):
        self.name = name
        self.status = BTStatus.RUNNING
        self.blackboard: Dict = {}
    
    @abstractmethod
    def tick(self) -> BTStatus:
        pass
    
    def reset(self):
        self.status = BTStatus.RUNNING


class Sequence(BTNode):
    """Execute children in order until one fails."""
    
    def __init__(self, name: str, children: List[BTNode]):
        super().__init__(name)
        self.children = children
        self.current_child = 0
    
    def tick(self) -> BTStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].tick()
            if status == BTStatus.RUNNING:
                return BTStatus.RUNNING
            elif status == BTStatus.FAILURE:
                self.current_child = 0
                return BTStatus.FAILURE
            else:
                self.current_child += 1
        self.current_child = 0
        return BTStatus.SUCCESS


class Fallback(BTNode):
    """Execute children until one succeeds."""
    
    def __init__(self, name: str, children: List[BTNode]):
        super().__init__(name)
        self.children = children
        self.current_child = 0
    
    def tick(self) -> BTStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].tick()
            if status == BTStatus.RUNNING:
                return BTStatus.RUNNING
            elif status == BTStatus.SUCCESS:
                self.current_child = 0
                return BTStatus.SUCCESS
            else:
                self.current_child += 1
        self.current_child = 0
        return BTStatus.FAILURE


class Condition(BTNode):
    """Condition node — checks blackboard."""
    
    def __init__(self, name: str, condition_fn: Callable[[Dict], bool]):
        super().__init__(name)
        self.condition_fn = condition_fn
    
    def tick(self) -> BTStatus:
        return BTStatus.SUCCESS if self.condition_fn(self.blackboard) else BTStatus.FAILURE


class Action(BTNode):
    """Action node — async operations."""
    
    def __init__(self, name: str, 
                 start_fn: Optional[Callable[[Dict], None]] = None,
                 check_fn: Optional[Callable[[Dict], BTStatus]] = None):
        super().__init__(name)
        self.start_fn = start_fn
        self.check_fn = check_fn
        self._started = False
    
    def tick(self) -> BTStatus:
        if not self._started and self.start_fn:
            self.start_fn(self.blackboard)
            self._started = True
        
        if self.check_fn:
            status = self.check_fn(self.blackboard)
            if status != BTStatus.RUNNING:
                self._started = False
            return status
        return BTStatus.SUCCESS


class CarbonCaptureBehaviorTree:
    """
    Behavior tree for autonomous carbon capture mission.
    
    Architecture:
        Root
        ├── Sequence: Capture Mission
        │   ├── Condition: CO2 detected above threshold
        │   ├── Sequence: Navigate to source
        │   │   ├── Action: Plan path
        │   │   ├── Action: Follow path
        │   │   └── Condition: Reached destination
        │   ├── Action: Deploy capture device
        │   └── Action: Monitor capture
        └── Fallback: Recovery
            ├── Condition: Battery > 20%
            ├── Action: Return to base
            └── Action: Emergency stop
    """
    
    def __init__(self, node: Node):
        self.node = node
        self.blackboard = {
            'robot_pose': None,
            'co2_concentration': 0.0,
            'battery_level': 100.0,
            'target_pose': None,
            'navigation_status': 'idle',
            'capture_status': 'idle',
            'mission_active': False,
        }
        self.tree = self._build_tree()
        self._lock = threading.Lock()
    
    def _build_tree(self) -> BTNode:
        capture_mission = Sequence('CaptureMission', [
            Condition('CO2Detected', 
                      lambda b: b['co2_concentration'] > 500.0),
            Sequence('NavigateToSource', [
                Action('PlanPath',
                       start_fn=self._plan_path,
                       check_fn=self._check_path_planned),
                Action('FollowPath',
                       start_fn=self._follow_path,
                       check_fn=self._check_navigation),
                Condition('ReachedDestination',
                          lambda b: b['navigation_status'] == 'arrived'),
            ]),
            Action('DeployCapture',
                   start_fn=self._deploy_capture,
                   check_fn=self._check_capture_deployed),
            Action('MonitorCapture',
                   start_fn=self._start_monitoring,
                   check_fn=self._check_capture_complete),
        ])
        
        recovery = Fallback('Recovery', [
            Condition('BatteryOK', 
                      lambda b: b['battery_level'] > 20.0),
            Action('ReturnToBase',
                   start_fn=self._return_to_base,
                   check_fn=self._check_returned),
            Action('EmergencyStop', 
                   start_fn=self._emergency_stop),
        ])
        
        root = Fallback('Root', [capture_mission, recovery])
        return root
    
    def tick(self) -> BTStatus:
        """Single tick of the behavior tree."""
        with self._lock:
            return self.tree.tick()
    
    def update_blackboard(self, key: str, value):
        """Update blackboard state."""
        with self._lock:
            self.blackboard[key] = value
    
    # ─── Action implementations ─────────────────────────────────────
    def _plan_path(self, bb: Dict):
        self.node.get_logger().info('Planning path to high CO2 zone…')
        bb['navigation_status'] = 'planning'
    
    def _check_path_planned(self, bb: Dict) -> BTStatus:
        if bb['navigation_status'] == 'planned':
            return BTStatus.SUCCESS
        elif bb['navigation_status'] == 'failed':
            return BTStatus.FAILURE
        return BTStatus.RUNNING
    
    def _follow_path(self, bb: Dict):
        self.node.get_logger().info('Following path…')
        bb['navigation_status'] = 'following'
    
    def _check_navigation(self, bb: Dict) -> BTStatus:
        if bb['navigation_status'] == 'arrived':
            return BTStatus.SUCCESS
        elif bb['navigation_status'] == 'failed':
            return BTStatus.FAILURE
        return BTStatus.RUNNING
    
    def _deploy_capture(self, bb: Dict):
        self.node.get_logger().info('Deploying capture device…')
        bb['capture_status'] = 'deploying'
    
    def _check_capture_deployed(self, bb: Dict) -> BTStatus:
        return BTStatus.SUCCESS if bb['capture_status'] == 'deployed' else BTStatus.RUNNING
    
    def _start_monitoring(self, bb: Dict):
        bb['capture_status'] = 'monitoring'
    
    def _check_capture_complete(self, bb: Dict) -> BTStatus:
        if bb.get('capture_complete', False):
            return BTStatus.SUCCESS
        return BTStatus.RUNNING
    
    def _return_to_base(self, bb: Dict):
        self.node.get_logger().warn('Returning to base…')
        bb['navigation_status'] = 'returning'
    
    def _check_returned(self, bb: Dict) -> BTStatus:
        return BTStatus.SUCCESS if bb['navigation_status'] == 'home' else BTStatus.RUNNING
    
    def _emergency_stop(self, bb: Dict):
        self.node.get_logger().error('EMERGENCY STOP')
        bb['mission_active'] = False


class MissionControllerNode(Node):
    """Mission controller using behavior tree."""
    
    def __init__(self):
        super().__init__('mission_controller')
        
        # ─── Behavior tree ──────────────────────────────────────────
        self.bt = CarbonCaptureBehaviorTree(self)
        
        # ─── Subscribers (decoupled from perception) ────────────────
        self.co2_sub = self.create_subscription(
            Float32, '/co2_concentration',
            lambda msg: self.bt.update_blackboard('co2_concentration', msg.data),
            10
        )
        
        self.battery_sub = self.create_subscription(
            Float32, '/battery_level',
            lambda msg: self.bt.update_blackboard('battery_level', msg.data),
            10
        )
        
        # ─── BT tick timer ──────────────────────────────────────────
        self.timer = self.create_timer(0.1, self._tick_bt)
        
        self.get_logger().info('MissionController ready (behavior tree)')
    
    def _tick_bt(self):
        status = self.bt.tick()
        if status == BTStatus.SUCCESS:
            self.get_logger().info('Mission complete')
        elif status == BTStatus.FAILURE:
            self.get_logger().warn('Mission failed')


def main(args=None):
    rclpy.init(args=args)
    node = MissionControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

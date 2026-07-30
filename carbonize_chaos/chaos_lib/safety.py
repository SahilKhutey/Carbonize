"""
Chaos safety controls and blast radius limiting
"""
import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict


logger = logging.getLogger(__name__)


@dataclass
class BlastRadiusConfig:
    """Configuration for blast radius limits."""
    max_concurrent_pods: int = 2
    max_percentage_pods: int = 50
    max_concurrent_services: int = 1
    exclude_namespaces: List[str] = field(default_factory=lambda: ['kube-system', 'monitoring'])
    exclude_labels: Dict[str, str] = field(default_factory=lambda: {'app': 'critical'})
    cooldown_between_experiments: int = 300
    max_experiments_per_hour: int = 10
    business_hours_only: bool = False
    require_approval: bool = False


class BlastRadiusLimiter:
    """Limits the blast radius of chaos experiments."""
    
    def __init__(self, config: Optional[BlastRadiusConfig] = None):
        self.config = config or BlastRadiusConfig()
        self._experiment_history: List[datetime] = []
        self._active_probes: Dict[str, datetime] = {}
    
    def can_inject(self, probe_config: Dict) -> bool:
        """Check if probe can be injected."""
        if not self._check_rate_limit():
            logger.warning("Rate limit exceeded")
            return False
        
        target_ns = probe_config.get('namespace', 'default')
        if target_ns in self.config.exclude_namespaces:
            logger.warning(f"Namespace {target_ns} excluded")
            return False
        
        return True
    
    def _check_rate_limit(self) -> bool:
        """Check if experiment rate limit is respected."""
        now = datetime.now()
        cutoff = now - timedelta(hours=1)
        self._experiment_history = [t for t in self._experiment_history if t > cutoff]
        
        if len(self._experiment_history) >= self.config.max_experiments_per_hour:
            return False
        
        return True
    
    def record_experiment(self, name: str):
        """Record that an experiment was started."""
        self._experiment_history.append(datetime.now())
        self._active_probes[name] = datetime.now()
    
    def complete_experiment(self, name: str):
        """Mark experiment as complete."""
        self._active_probes.pop(name, None)


class SafetyController:
    """Global safety controller for chaos experiments."""
    
    def __init__(self):
        self._global_abort_flag = False
        self._active_experiments: Dict[str, datetime] = {}
        self._max_concurrent_experiments = 1
    
    def is_experiment_safe(self, experiment) -> bool:
        """Check if experiment is safe to run."""
        if self._global_abort_flag:
            logger.error("Global abort flag is set")
            return False
        
        return True
    
    def global_abort(self):
        """Trigger global abort of all chaos experiments."""
        logger.warning("GLOBAL ABORT triggered")
        self._global_abort_flag = True
    
    def reset(self):
        """Reset safety state."""
        self._global_abort_flag = False

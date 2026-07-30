"""
Base chaos probe interface
"""
import asyncio
import logging
import time
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import traceback


logger = logging.getLogger(__name__)


class ProbeStatus(Enum):
    PENDING = "pending"
    INJECTING = "injecting"
    ACTIVE = "active"
    REMEDIATING = "remediating"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class ProbeResult:
    """Result of a chaos probe execution."""
    probe_name: str
    status: ProbeStatus
    started_at: float
    completed_at: Optional[float] = None
    injection_success: bool = False
    recovery_success: bool = False
    steady_state_maintained: bool = True
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    observations: List[Dict] = field(default_factory=list)
    slo_violations: List[Dict] = field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        if self.completed_at:
            return self.completed_at - self.started_at
        return time.time() - self.started_at


class ChaosProbe(ABC):
    """Abstract base class for all chaos probes."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.status = ProbeStatus.PENDING
        self.result = ProbeResult(
            probe_name=name,
            status=ProbeStatus.PENDING,
            started_at=time.time(),
        )
        self._safety_checks: List[Callable] = []
        self._abort_flag = False
    
    @abstractmethod
    async def inject(self) -> bool:
        """Inject the chaos. Returns True if successful."""
        pass
    
    @abstractmethod
    async def remediate(self) -> bool:
        """Recover from the chaos. Returns True if successful."""
        pass
    
    @abstractmethod
    async def validate_pre_condition(self) -> bool:
        """Check if system is in steady state before chaos."""
        pass
    
    @abstractmethod
    async def validate_post_condition(self) -> bool:
        """Check if system recovers after chaos."""
        pass
    
    def add_safety_check(self, check: Callable):
        """Add a safety check function."""
        self._safety_checks.append(check)
    
    async def run_safety_checks(self) -> bool:
        """Run all safety checks."""
        for check in self._safety_checks:
            try:
                if not await check():
                    return False
            except Exception as e:
                logger.error(f"Safety check failed: {e}")
                return False
        return True
    
    def abort(self):
        """Signal abort."""
        self._abort_flag = True
    
    async def execute(self) -> ProbeResult:
        """Execute the full chaos probe lifecycle."""
        self.status = ProbeStatus.INJECTING
        self.result.started_at = time.time()
        
        try:
            # ─── Pre-flight ─────────────────────────────────────
            logger.info(f"=== Probe {self.name} starting ===")
            
            if not await self.run_safety_checks():
                logger.error(f"Safety checks failed for {self.name}")
                self.result.status = ProbeStatus.FAILED
                self.result.errors.append("Safety checks failed")
                return self.result
            
            if not await self.validate_pre_condition():
                logger.error(f"Pre-condition failed for {self.name}")
                self.result.status = ProbeStatus.FAILED
                self.result.errors.append("Pre-condition not met")
                return self.result
            
            # ─── Inject chaos ────────────────────────────────────
            logger.info(f"Injecting chaos: {self.name}")
            self.result.injection_success = await self.inject()
            
            if not self.result.injection_success:
                logger.error(f"Failed to inject {self.name}")
                self.result.status = ProbeStatus.FAILED
                return self.result
            
            self.status = ProbeStatus.ACTIVE
            
            # ─── Duration ────────────────────────────────────────
            duration = self.config.get('duration', 60)
            logger.info(f"Chaos active for {duration}s")
            
            # ─── Monitor during chaos ────────────────────────────
            await self._monitor_during_chaos(duration)
            
            # ─── Remediate ───────────────────────────────────────
            self.status = ProbeStatus.REMEDIATING
            logger.info(f"Remediating: {self.name}")
            self.result.recovery_success = await self.remediate()
            
            if not self.result.recovery_success:
                logger.error(f"Failed to remediate {self.name}")
                self.result.errors.append("Remediation failed")
                # CRITICAL: Force remediation
                await self._force_remediation()
            
            # ─── Validate recovery ───────────────────────────────
            self.result.steady_state_maintained = await self.validate_post_condition()
            self.result.status = ProbeStatus.COMPLETED if self.result.recovery_success else ProbeStatus.FAILED
            self.result.completed_at = time.time()
            
            logger.info(
                f"=== Probe {self.name} completed: "
                f"injection={'OK' if self.result.injection_success else 'FAIL'} "
                f"recovery={'OK' if self.result.recovery_success else 'FAIL'} "
                f"steady_state={'OK' if self.result.steady_state_maintained else 'VIOLATED'} ==="
            )
        
        except Exception as e:
            logger.exception(f"Probe {self.name} crashed: {e}")
            self.result.status = ProbeStatus.FAILED
            self.result.errors.append(f"Exception: {str(e)}")
            self.result.observations.append({
                'timestamp': time.time(),
                'type': 'exception',
                'message': str(e),
                'traceback': traceback.format_exc(),
            })
            # Emergency remediation
            await self._force_remediation()
        
        return self.result
    
    async def _monitor_during_chaos(self, duration: int):
        """Monitor system during chaos injection."""
        check_interval = self.config.get('check_interval', 5)
        start_time = time.time()
        
        while time.time() - start_time < duration:
            if self._abort_flag:
                logger.warning(f"Abort signaled for {self.name}")
                break
            
            # ─── Check SLOs ─────────────────────────────────────
            try:
                slo_violations = await self._check_slos()
                if slo_violations:
                    self.result.slo_violations.extend(slo_violations)
                    logger.warning(f"SLO violations detected: {slo_violations}")
            except Exception as e:
                logger.error(f"SLO check failed: {e}")
            
            await asyncio.sleep(check_interval)
    
    async def _check_slos(self) -> List[Dict]:
        """Check SLOs during chaos. Override in subclasses."""
        return []
    
    async def _force_remediation(self):
        """Force remediation regardless of state."""
        logger.warning(f"Force remediation for {self.name}")
        try:
            await self.remediate()
        except Exception as e:
            logger.error(f"Force remediation failed: {e}")

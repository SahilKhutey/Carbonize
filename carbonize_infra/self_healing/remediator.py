"""
Production Self-Healing System
Automatically detects and remediates common issues.
"""

import asyncio
import time
import logging
import subprocess
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import httpx
try:
    import docker
except ImportError:
    docker = None


class IssueType(Enum):
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_LATENCY = "high_latency"
    OOM_KILLED = "oom_killed"
    MODEL_INFERENCE_FAILED = "model_inference_failed"
    DISK_FULL = "disk_full"
    CERTIFICATE_EXPIRING = "certificate_expiring"
    SERVICE_DOWN = "service_down"
    DEADLOCK = "deadlock"
    ZOMBIE_PROCESS = "zombie_process"


@dataclass
class Issue:
    """Detected issue."""
    issue_type: IssueType
    severity: str            # 'low', 'medium', 'high', 'critical'
    detected_at: float
    resource: str
    description: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class RemediationAction:
    """Action to take to remediate an issue."""
    name: str
    action_type: str          # 'restart', 'scale', 'cleanup', 'notify'
    params: Dict
    cooldown_sec: float = 300
    last_executed: float = 0.0
    success_count: int = 0
    failure_count: int = 0


class SelfHealingEngine:
    """
    Detects issues and executes remediations automatically.
    
    Safety:
        - Cooldown periods prevent remediation storms
        - Escalation to humans on persistent issues
        - Dry-run mode for testing
    """
    
    def __init__(self, dry_run: bool = False, 
                 alert_webhook: Optional[str] = None):
        self.dry_run = dry_run
        self.alert_webhook = alert_webhook
        self.logger = logging.getLogger('self-healing')
        self._actions: Dict[IssueType, List[RemediationAction]] = {}
        self._metrics = httpx.AsyncClient(timeout=10)
        if docker:
            try:
                self._docker_client = docker.from_env()
            except Exception:
                self._docker_client = None
        else:
            self._docker_client = None
        self._issues: List[Issue] = []
        self._running = False
    
    def register_remediation(self, issue_type: IssueType,
                            action: RemediationAction):
        """Register remediation action for an issue type."""
        if issue_type not in self._actions:
            self._actions[issue_type] = []
        self._actions[issue_type].append(action)
    
    async def start_monitoring(self):
        """Start the monitoring loop."""
        self._running = True
        while self._running:
            try:
                await self._monitoring_cycle()
            except Exception as e:
                self.logger.exception(f"Monitoring cycle failed: {e}")
            await asyncio.sleep(30)
    
    async def _monitoring_cycle(self):
        """Single monitoring cycle."""
        issues = []
        
        issues.extend(await self._check_error_rate())
        issues.extend(await self._check_latency())
        issues.extend(await self._check_disk_space())
        issues.extend(await self._check_service_health())
        issues.extend(await self._check_certificates())
        issues.extend(await self._check_zombie_processes())
        
        for issue in issues:
            await self._remediate(issue)
    
    async def _check_error_rate(self) -> List[Issue]:
        """Check error rate via Prometheus."""
        try:
            response = await self._metrics.get(
                "http://prometheus:9090/api/v1/query",
                params={
                    'query': 'rate(carbonize_inference_total{status="failed"}[5m]) / '
                            'rate(carbonize_inference_total[5m])'
                }
            )
            data = response.json()
            
            issues = []
            for result in data.get('data', {}).get('result', []):
                error_rate = float(result['value'][1])
                if error_rate > 0.10:
                    issues.append(Issue(
                        issue_type=IssueType.HIGH_ERROR_RATE,
                        severity='high' if error_rate > 0.30 else 'medium',
                        detected_at=time.time(),
                        resource=result['metric'].get('service', 'unknown'),
                        description=f"Error rate {error_rate*100:.1f}%",
                        metadata={'error_rate': error_rate}
                    ))
            return issues
        except Exception:
            return []
    
    async def _check_latency(self) -> List[Issue]:
        """Check p99 latency."""
        try:
            response = await self._metrics.get(
                "http://prometheus:9090/api/v1/query",
                params={
                    'query': 'histogram_quantile(0.99, '
                            'rate(carbonize_inference_latency_seconds_bucket[5m])) * 1000'
                }
            )
            data = response.json()
            
            issues = []
            for result in data.get('data', {}).get('result', []):
                latency = float(result['value'][1])
                if latency > 500:
                    issues.append(Issue(
                        issue_type=IssueType.HIGH_LATENCY,
                        severity='high' if latency > 1000 else 'medium',
                        detected_at=time.time(),
                        resource=result['metric'].get('service', 'unknown'),
                        description=f"p99 latency {latency:.0f}ms",
                        metadata={'latency_ms': latency}
                    ))
            return issues
        except Exception:
            return []
    
    async def _check_disk_space(self) -> List[Issue]:
        """Check disk usage on all hosts."""
        try:
            result = subprocess.run(
                ['df', '-h', '--output=pcent,target'],
                capture_output=True, text=True, timeout=5
            )
            issues = []
            for line in result.stdout.split('\n')[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    pct_str = parts[0].rstrip('%')
                    try:
                        pct = int(pct_str)
                        if pct > 90:
                            issues.append(Issue(
                                issue_type=IssueType.DISK_FULL,
                                severity='critical' if pct > 95 else 'high',
                                detected_at=time.time(),
                                resource=parts[1],
                                description=f"Disk usage {pct}%",
                                metadata={'usage_percent': pct}
                            ))
                    except ValueError:
                        pass
            return issues
        except Exception:
            return []
    
    async def _check_service_health(self) -> List[Issue]:
        """Check service health endpoints."""
        services = [
            ('backend', 'http://carbonize-backend:8000/v1/health/ready'),
            ('inference', 'http://carbonize-inference:9090/health'),
            ('ros-bridge', 'http://carbonize-ros-bridge:9090/health'),
        ]
        
        issues = []
        for name, url in services:
            try:
                response = await self._metrics.get(url, timeout=3)
                if response.status_code != 200:
                    issues.append(Issue(
                        issue_type=IssueType.SERVICE_DOWN,
                        severity='critical',
                        detected_at=time.time(),
                        resource=name,
                        description=f"Health check returned {response.status_code}",
                        metadata={'status_code': response.status_code}
                    ))
            except Exception as e:
                issues.append(Issue(
                    issue_type=IssueType.SERVICE_DOWN,
                    severity='critical',
                    detected_at=time.time(),
                    resource=name,
                    description=f"Service unreachable: {str(e)[:100]}",
                ))
        return issues
    
    async def _check_certificates(self) -> List[Issue]:
        """Check TLS certificate expiration."""
        try:
            import ssl
            import socket
            
            issues = []
            for hostname in ['api.carbonize.io', 'dashboard.carbonize.io']:
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, 443), timeout=5) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert = ssock.getpeercert()
                            from datetime import datetime
                            expiry = datetime.strptime(
                                cert['notAfter'], '%b %d %H:%M:%S %Y %Z'
                            )
                            days_until_expiry = (expiry - datetime.utcnow()).days
                            
                            if days_until_expiry < 14:
                                issues.append(Issue(
                                    issue_type=IssueType.CERTIFICATE_EXPIRING,
                                    severity='high' if days_until_expiry < 7 else 'medium',
                                    detected_at=time.time(),
                                    resource=hostname,
                                    description=f"Cert expires in {days_until_expiry} days",
                                    metadata={'days_remaining': days_until_expiry}
                                ))
                except Exception:
                    pass
            return issues
        except Exception:
            return []
    
    async def _check_zombie_processes(self) -> List[Issue]:
        """Check for zombie processes."""
        try:
            result = subprocess.run(
                ['ps', '-eo', 'stat,pid,comm', '--no-headers'],
                capture_output=True, text=True, timeout=5
            )
            issues = []
            zombie_count = sum(1 for line in result.stdout.split('\n') 
                              if line.startswith('Z'))
            if zombie_count > 50:
                issues.append(Issue(
                    issue_type=IssueType.ZOMBIE_PROCESS,
                    severity='medium',
                    detected_at=time.time(),
                    resource='system',
                    description=f"{zombie_count} zombie processes",
                    metadata={'zombie_count': zombie_count}
                ))
            return issues
        except Exception:
            return []
    
    async def _remediate(self, issue: Issue):
        """Execute remediation for an issue."""
        actions = self._actions.get(issue.issue_type, [])
        if not actions:
            self.logger.warning(f"No remediation registered for {issue.issue_type}")
            return
        
        for action in actions:
            if time.time() - action.last_executed < action.cooldown_sec:
                self.logger.info(
                    f"Skipping {action.name} for {issue.issue_type} "
                    f"(cooldown active)"
                )
                continue
            
            self.logger.info(
                f"Executing remediation: {action.name} for {issue.issue_type}"
            )
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would execute: {action.action_type}")
                continue
            
            try:
                success = await self._execute_action(action, issue)
                action.last_executed = time.time()
                
                if success:
                    action.success_count += 1
                    self.logger.info(f"Remediation succeeded: {action.name}")
                    await self._send_alert(
                        f"✅ Self-healed: {issue.description}",
                        action_name=action.name,
                        issue=issue
                    )
                else:
                    action.failure_count += 1
                    self.logger.error(f"Remediation failed: {action.name}")
                    
                    if action.failure_count >= 3:
                        await self._send_alert(
                            f"🚨 Remediation failed 3 times: {issue.description}",
                            severity='critical',
                            action_name=action.name,
                            issue=issue
                        )
            except Exception as e:
                self.logger.exception(f"Remediation exception: {e}")
                action.failure_count += 1
    
    async def _execute_action(self, action: RemediationAction, 
                            issue: Issue) -> bool:
        """Execute specific remediation action."""
        if action.action_type == 'restart_container':
            return self._restart_container(action.params['container_name'])
        elif action.action_type == 'cleanup_disk':
            return self._cleanup_disk(action.params['path'])
        else:
            return False
    
    def _restart_container(self, container_name: str) -> bool:
        if not self._docker_client:
            return False
        try:
            container = self._docker_client.containers.get(container_name)
            container.restart(timeout=30)
            return True
        except Exception:
            return False
    
    def _cleanup_disk(self, path: str) -> bool:
        try:
            subprocess.run(['find', '/var/log/carbonize', '-name', '*.log', 
                          '-mtime', '+7', '-delete'],
                         timeout=30, capture_output=True)
            return True
        except Exception:
            return False
    
    async def _send_alert(self, message: str, severity: str = 'info',
                         **kwargs):
        """Send alert to webhook."""
        if not self.alert_webhook:
            return
        
        payload = {
            'message': message,
            'severity': severity,
            'timestamp': time.time(),
            'source': 'carbonize-self-healing',
            **kwargs
        }
        
        try:
            await self._metrics.post(self.alert_webhook, json=payload)
        except Exception as e:
            self.logger.error(f"Failed to send alert: {e}")

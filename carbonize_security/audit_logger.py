"""
Production Audit Logging System
"""

import json
import time
import hashlib
import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import gzip
import os
from datetime import datetime, timedelta
from cryptography.fernet import Fernet


class AuditEvent(Enum):
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    MODEL_PROMOTED = "model_promoted"
    MODEL_ROLLBACK = "model_rollback"
    CONFIG_CHANGED = "config_changed"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    DATA_ACCESSED = "data_accessed"
    DATA_MODIFIED = "data_modified"
    DATA_DELETED = "data_deleted"
    ADMIN_LOGIN = "admin_login"
    SENSITIVE_OPERATION = "sensitive_operation"


@dataclass
class AuditLog:
    """Immutable audit log entry."""
    event_type: AuditEvent
    timestamp: float
    principal_id: str
    principal_role: str
    request_id: str
    source_ip: str
    user_agent: str
    action: str
    resource: str
    outcome: str    # 'success', 'failure'
    details: Dict[str, Any] = field(default_factory=dict)
    previous_hash: Optional[str] = None
    log_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['event_type'] = self.event_type.value
        d['timestamp_iso'] = datetime.utcfromtimestamp(self.timestamp).isoformat()
        return d


class AuditLogger:
    """
    Tamper-evident audit logging with hash chaining.
    
    Each log entry includes:
        - Hash of previous entry (chain integrity)
        - Hash of current entry content
        - Encryption at rest
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None,
                 s3_bucket: Optional[str] = None,
                 log_dir: str = 'logs/audit',
                 retention_days: int = 365):
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        self.s3_bucket = s3_bucket
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        
        self._last_hash: Optional[str] = None
        self._load_last_hash()
    
    def _load_last_hash(self):
        """Load hash of most recent log entry to continue chain."""
        chain_file = self.log_dir / 'chain.json'
        if chain_file.exists():
            with open(chain_file, 'r') as f:
                data = json.load(f)
                self._last_hash = data.get('last_hash')
    
    def _save_last_hash(self):
        """Persist current last hash."""
        chain_file = self.log_dir / 'chain.json'
        with open(chain_file, 'w') as f:
            json.dump({'last_hash': self._last_hash}, f)
    
    def log(self, event: AuditLog) -> None:
        """Write audit log entry with hash chaining."""
        event.previous_hash = self._last_hash
        event.log_hash = self._compute_hash(event)
        self._last_hash = event.log_hash
        
        log_json = json.dumps(event.to_dict())
        encrypted = self.cipher.encrypt(log_json.encode())
        
        today = datetime.utcfromtimestamp(event.timestamp).strftime('%Y-%m-%d')
        log_file = self.log_dir / f"audit-{today}.log.gz"
        
        with gzip.open(log_file, 'at') as f:
            f.write(encrypted.decode() + '\n')
        
        self._save_last_hash()
    
    def _compute_hash(self, event: AuditLog) -> str:
        """Compute SHA-256 hash of log entry."""
        content = json.dumps({
            'event_type': event.event_type.value,
            'timestamp': event.timestamp,
            'principal_id': event.principal_id,
            'action': event.action,
            'resource': event.resource,
            'outcome': event.outcome,
            'previous_hash': event.previous_hash,
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_chain(self, log_file: Path) -> bool:
        """Verify integrity of log chain."""
        previous_hash = None
        
        with gzip.open(log_file, 'rt') as f:
            for line in f:
                entry = json.loads(self.cipher.decrypt(line.strip().encode()).decode())
                
                if previous_hash != entry.get('previous_hash'):
                    return False
                
                content = json.dumps({
                    'event_type': entry['event_type'],
                    'timestamp': entry['timestamp'],
                    'principal_id': entry['principal_id'],
                    'action': entry['action'],
                    'resource': entry['resource'],
                    'outcome': entry['outcome'],
                    'previous_hash': entry['previous_hash'],
                }, sort_keys=True)
                expected_hash = hashlib.sha256(content.encode()).hexdigest()
                
                if entry.get('log_hash') != expected_hash:
                    return False
                
                previous_hash = entry['log_hash']
        
        return True

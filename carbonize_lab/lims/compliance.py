"""
Compliance & Audit Trail Logger
"""
import hashlib
from datetime import datetime
from typing import Dict, List


class AuditTrailLogger:
    def __init__(self):
        self.logs: List[Dict] = []

    def log_action(self, user: str, action: str, entity_type: str, entity_id: str, details: Dict = None) -> Dict:
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user': user,
            'action': action,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'details': details or {},
        }
        entry['hash'] = hashlib.sha256(str(entry).encode()).hexdigest()
        self.logs.append(entry)
        return entry

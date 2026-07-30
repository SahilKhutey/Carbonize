"""
Chaos experiment reporter
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ChaosReporter:
    """Generates chaos experiment reports."""
    
    def __init__(self, output_dir: str = './results/chaos'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_report(self, result, experiment):
        """Generate comprehensive report."""
        timestamp = datetime.fromtimestamp(result.started_at).strftime('%Y%m%d_%H%M%S')
        report_name = f"{experiment.name}_{timestamp}"
        
        json_path = self.output_dir / f"{report_name}.json"
        with open(json_path, 'w') as f:
            json.dump({
                'experiment': {
                    'name': experiment.name,
                    'description': experiment.description,
                    'hypothesis': experiment.hypothesis,
                    'duration': experiment.duration,
                    'tags': experiment.tags,
                },
                'result': {
                    'status': result.status.value,
                    'hypothesis_validated': result.hypothesis_validated,
                    'hypothesis_result': result.hypothesis_result,
                    'started_at': result.started_at,
                    'completed_at': result.completed_at,
                    'total_slo_violations': result.total_slo_violations,
                    'recovery_time_seconds': result.recovery_time_seconds,
                    'resilience_score': result.resilience_score,
                    'rollback_triggered': result.rollback_triggered,
                },
            }, f, indent=2)
        
        md_path = self.output_dir / f"{report_name}.md"
        md = f"# Chaos Engineering Report: {experiment.name}\n\nResilience Score: {result.resilience_score:.1f}/100\n"
        md_path.write_text(md)
        
        logger.info(f"Report generated: {json_path}")

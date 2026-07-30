"""
Production A/B Testing Framework for ML Models
"""

import asyncio
import random
import hashlib
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
from collections import defaultdict
import numpy as np
from scipy import stats
import logging
import json
from pathlib import Path


class ExperimentStatus(Enum):
    DRAFT = "DRAFT"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


@dataclass
class ExperimentVariant:
    """A single model variant in the experiment."""
    name: str
    model_uri: str
    traffic_weight: float = 0.5    # 0.0 to 1.0
    is_control: bool = False
    metadata: Dict = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """Statistical analysis results."""
    is_significant: bool
    p_value: float
    effect_size: float
    confidence_interval: Tuple[float, float]
    winner: Optional[str]
    recommendation: str


@dataclass
class PredictionEvent:
    """Logged prediction event for analysis."""
    experiment_id: str
    variant_name: str
    user_id: str
    timestamp: float
    inference_time_ms: float
    confidence: float
    prediction: Dict
    ground_truth: Optional[Dict] = None
    user_feedback: Optional[float] = None    # 0.0 to 1.0


class ABTestFramework:
    """
    Production A/B testing for ML models.
    
    Features:
        - Deterministic assignment (same user always sees same variant)
        - Traffic splitting with weighted random
        - Statistical significance testing
        - Early stopping on harmful variants
    """
    
    def __init__(self, storage_backend='redis'):
        self.experiments: Dict[str, 'ABExperiment'] = {}
        self.logger = logging.getLogger('ab-testing')
    
    def create_experiment(
        self,
        experiment_id: str,
        variants: List[ExperimentVariant],
        description: str = "",
        success_metric: str = 'mAP50',
        min_samples_per_variant: int = 1000,
        max_runtime_days: int = 14,
    ) -> 'ABExperiment':
        """Create new A/B experiment."""
        total_weight = sum(v.traffic_weight for v in variants)
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Traffic weights must sum to 1.0, got {total_weight}")
        
        control_count = sum(1 for v in variants if v.is_control)
        if control_count != 1:
            raise ValueError(f"Exactly one variant must be control, got {control_count}")
        
        experiment = ABExperiment(
            id=experiment_id,
            variants=variants,
            description=description,
            success_metric=success_metric,
            min_samples=min_samples_per_variant,
            max_runtime_days=max_runtime_days,
            framework=self
        )
        
        self.experiments[experiment_id] = experiment
        return experiment
    
    def assign_variant(self, experiment_id: str, 
                       user_id: str) -> Optional[ExperimentVariant]:
        """Deterministically assign user to variant."""
        if experiment_id not in self.experiments:
            return None
        
        experiment = self.experiments[experiment_id]
        if experiment.status != ExperimentStatus.RUNNING:
            return experiment.get_default_variant()
        
        hash_input = f"{experiment_id}:{user_id}".encode()
        hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16)
        assignment = (hash_value % 10000) / 10000.0
        
        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.traffic_weight
            if assignment < cumulative:
                return variant
        
        return experiment.variants[-1]


class ABExperiment:
    """Individual A/B experiment."""
    
    def __init__(self, id: str, variants: List[ExperimentVariant],
                 description: str, success_metric: str,
                 min_samples: int, max_runtime_days: int,
                 framework: ABTestFramework):
        self.id = id
        self.variants = variants
        self.description = description
        self.success_metric = success_metric
        self.min_samples = min_samples
        self.max_runtime_days = max_runtime_days
        self.framework = framework
        self.status = ExperimentStatus.DRAFT
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.events: List[PredictionEvent] = []
        self._lock = asyncio.Lock()
    
    def start(self):
        """Start the experiment."""
        if self.status != ExperimentStatus.DRAFT:
            raise RuntimeError(f"Cannot start experiment in status {self.status}")
        self.status = ExperimentStatus.RUNNING
        self.start_time = time.time()
    
    def pause(self):
        self.status = ExperimentStatus.PAUSED
    
    def complete(self):
        self.status = ExperimentStatus.COMPLETED
        self.end_time = time.time()
    
    def log_event(self, event: PredictionEvent):
        """Log prediction event."""
        if event.experiment_id != self.id:
            raise ValueError("Event experiment_id mismatch")
        self.events.append(event)
    
    def get_default_variant(self) -> ExperimentVariant:
        """Return control variant."""
        for v in self.variants:
            if v.is_control:
                return v
        return self.variants[0]
    
    def analyze(self) -> ExperimentResult:
        """Statistical analysis of experiment results."""
        variant_data = defaultdict(list)
        for event in self.events:
            if event.user_feedback is not None:
                variant_data[event.variant_name].append(event.user_feedback)
            elif event.ground_truth is not None:
                correct = event.prediction.get('class') == event.ground_truth.get('class')
                variant_data[event.variant_name].append(1.0 if correct else 0.0)
        
        control_variant = self.get_default_variant()
        control_data = variant_data.get(control_variant.name, [])
        
        if len(control_data) < self.min_samples:
            return ExperimentResult(
                is_significant=False,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                winner=None,
                recommendation=f"Need {self.min_samples - len(control_data)} more control samples"
            )
        
        results = []
        for variant in self.variants:
            if variant.is_control:
                continue
            
            variant_results = variant_data.get(variant.name, [])
            if len(variant_results) < self.min_samples:
                continue
            
            t_stat, p_value = stats.ttest_ind(control_data, variant_results, equal_var=False)
            
            pooled_std = np.sqrt(
                (np.std(control_data)**2 + np.std(variant_results)**2) / 2
            )
            effect_size = (np.mean(variant_results) - np.mean(control_data)) / max(pooled_std, 0.001)
            
            diff = np.mean(variant_results) - np.mean(control_data)
            se = np.sqrt(
                np.var(control_data)/len(control_data) + 
                np.var(variant_results)/len(variant_results)
            )
            ci = (diff - 1.96 * se, diff + 1.96 * se)
            
            results.append({
                'variant': variant.name,
                'p_value': float(p_value),
                'effect_size': float(effect_size),
                'ci': ci,
                'mean_diff': float(diff),
                'n_samples': len(variant_results)
            })
        
        winner = None
        best_improvement = 0.0
        for r in results:
            if r['p_value'] < 0.05 and r['mean_diff'] > best_improvement:
                winner = r['variant']
                best_improvement = r['mean_diff']
        
        if winner:
            recommendation = f"Promote variant '{winner}' to production (p<0.05, +{best_improvement*100:.1f}%)"
        elif any(r['p_value'] < 0.05 for r in results):
            wrong_direction = next((r for r in results if r['p_value'] < 0.05 and r['mean_diff'] < 0), None)
            if wrong_direction:
                recommendation = f"REJECT: Variant '{wrong_direction['variant']}' performs worse"
            else:
                recommendation = "No clear winner — continue experiment"
        else:
            recommendation = "No significant difference detected"
        
        if results:
            primary = results[0]
            return ExperimentResult(
                is_significant=primary['p_value'] < 0.05,
                p_value=primary['p_value'],
                effect_size=primary['effect_size'],
                confidence_interval=primary['ci'],
                winner=winner,
                recommendation=recommendation
            )
        else:
            return ExperimentResult(
                is_significant=False,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                winner=None,
                recommendation="Insufficient data"
            )
    
    def should_stop_early(self) -> Tuple[bool, str]:
        """Check if experiment should stop early."""
        if self.start_time:
            elapsed_days = (time.time() - self.start_time) / 86400
            if elapsed_days > self.max_runtime_days:
                return True, "Maximum runtime exceeded"
        
        sample_counts = defaultdict(int)
        for event in self.events:
            sample_counts[event.variant_name] += 1
        
        for variant in self.variants:
            if sample_counts[variant.name] < self.min_samples:
                return False, "Still collecting samples"
        
        result = self.analyze()
        if result.is_significant and result.winner:
            return True, f"Significant winner found: {result.winner}"
        
        if result.effect_size < -0.3 and result.p_value < 0.05:
            return True, "Variant showing significant negative effect"
        
        return False, "Continue"

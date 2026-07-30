"""
Bill of Materials (BOM) Calculator
"""
from typing import Dict, List

def generate_deployment_bom(tier: str = 'medium') -> List[Dict]:
    return [
        {'component': 'Kubernetes Control Plane', 'provider': 'EKS / GKE', 'nodes': 3, 'cost_usd_mo': 400},
        {'component': 'ML Inference Nodes (MACE/PaiNN)', 'provider': 'NVIDIA A10G / L4', 'count': 4, 'cost_usd_mo': 1800},
        {'component': 'Kafka & Flink Event Stream', 'provider': 'MSK / Confluent', 'cluster_size': '3-node', 'cost_usd_mo': 600},
        {'component': 'TimescaleDB Telemetry Store', 'provider': 'Managed PG', 'storage_gb': 2000, 'cost_usd_mo': 600},
    ]

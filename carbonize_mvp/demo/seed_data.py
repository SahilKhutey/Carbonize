"""
Pre-seeded demo data for Carbonize MVP
Generates 12 months of plant data, 12,000 solvents, lab results, chaos drills, ROI scenarios.
"""
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np


class DemoSeedData:
    """Generate all demo data once at startup."""
    
    @staticmethod
    def generate_solvent_portfolio() -> List[Dict]:
        """Generate 12,000 virtual amine candidates with predictions."""
        functional_groups = [
            'primary_amine', 'secondary_amine', 'tertiary_amine',
            'sterically_hindered', 'cyclic_amine', 'amino_acid',
            'amino_alcohol', 'polyamine', 'quaternary_ammonium',
            'guanidine', 'imidazole', 'piperazine', 'morpholine',
        ]
        
        backbones = [
            'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8',
            'ethyl', 'propyl', 'butyl', 'cyclohexyl', 'phenyl',
            'alkanol', 'alkanolamine', 'aminoether',
        ]
        
        substituents = [
            'H', 'CH3', 'OH', 'OCH3', 'NH2', 'NHCH3', 'COOH',
            'Cl', 'F', 'Br', 'C2H5', 'C3H7', 'phenyl', 'CF3',
        ]
        
        solvents = []
        solvent_id = 0
        
        for fg in functional_groups:
            for backbone in backbones:
                for sub in substituents:
                    if random.random() > 0.7:
                        continue
                    
                    is_primary = (fg == 'primary_amine')
                    is_hindered = (fg == 'sterically_hindered')
                    is_piperazine = (fg == 'piperazine')
                    
                    mw = 50 + random.uniform(20, 100)
                    if len(backbone) > 4:
                        mw += 30
                    
                    base_loading = 0.5
                    if is_primary:
                        base_loading = 0.55
                    elif is_hindered:
                        base_loading = 0.45
                    elif is_piperazine:
                        base_loading = 0.62
                    elif fg == 'tertiary_amine':
                        base_loading = 0.75
                    
                    loading = base_loading + random.gauss(0, 0.05)
                    loading = max(0.1, min(1.2, loading))
                    
                    cyclic_capacity = loading * 0.75 + random.gauss(0, 0.02)
                    cyclic_capacity = max(0.1, min(0.8, cyclic_capacity))
                    
                    if is_primary:
                        base_dH = 85.0
                    elif is_hindered:
                        base_dH = 65.0
                    elif is_piperazine:
                        base_dH = 70.0
                    elif fg == 'tertiary_amine':
                        base_dH = 58.0
                    else:
                        base_dH = 75.0
                    
                    dH = base_dH + random.gauss(0, 5)
                    dH = max(30, min(120, dH))
                    
                    if is_primary:
                        rate = 50 + random.gauss(0, 10)
                    elif is_hindered:
                        rate = 5 + random.gauss(0, 2)
                    elif is_piperazine:
                        rate = 80 + random.gauss(0, 15)
                    else:
                        rate = 20 + random.gauss(0, 5)
                    rate = max(0.1, rate)
                    
                    if is_primary:
                        deg = 0.15 + random.gauss(0, 0.03)
                    elif is_hindered:
                        deg = 0.02 + random.gauss(0, 0.01)
                    elif is_piperazine:
                        deg = 0.05 + random.gauss(0, 0.01)
                    elif fg == 'tertiary_amine':
                        deg = 0.03 + random.gauss(0, 0.01)
                    else:
                        deg = 0.08 + random.gauss(0, 0.02)
                    deg = max(0.001, deg)
                    
                    if fg == 'primary_amine':
                        tox = 1500 + random.gauss(0, 300)
                    elif is_hindered:
                        tox = 2500 + random.gauss(0, 400)
                    else:
                        tox = 2000 + random.gauss(0, 500)
                    tox = max(500, min(5000, tox))
                    
                    cost = 2.0 + random.uniform(0, 20)
                    if 'phenyl' in backbone or 'cyclohexyl' in backbone:
                        cost += 5
                    if sub in ['F', 'Cl', 'Br', 'CF3']:
                        cost += 3
                    
                    bp = 350 + mw * 1.5 + random.gauss(0, 10)
                    bp = max(300, min(550, bp))
                    
                    visc = 1.0 + random.uniform(0, 5)
                    if mw > 100:
                        visc += 1
                    
                    s_loading = min(100, loading * 130)
                    s_cyclic = min(100, cyclic_capacity * 200)
                    s_dH = max(0, 100 - (dH - 40) * 0.8)
                    s_rate = min(100, rate * 1.5)
                    s_deg = max(0, 100 - deg * 400)
                    s_tox = min(100, tox / 30)
                    s_cost = max(0, 100 - cost * 8)
                    s_purity = 70 + random.gauss(0, 10)
                    
                    overall_score = (
                        0.20 * s_loading +
                        0.15 * s_cyclic +
                        0.15 * s_dH +
                        0.10 * s_rate +
                        0.10 * s_deg +
                        0.05 * s_tox +
                        0.05 * s_cost +
                        0.20 * s_purity
                    )
                    overall_score = max(0, min(100, overall_score))
                    
                    synthesis_done = (overall_score > 85 and random.random() > 0.6)
                    lab_tested = synthesis_done and random.random() > 0.4
                    
                    solvents.append({
                        'id': f'SOLV-{solvent_id:04d}',
                        'name': f'A{fg[0].upper()}{solvent_id:04d}',
                        'functional_group': fg,
                        'backbone': backbone,
                        'substituent': sub,
                        'smiles': f'({fg})({backbone})({sub})',
                        'molecular_weight': round(mw, 2),
                        'boiling_point': round(bp, 1),
                        'viscosity_mPa_s': round(visc, 2),
                        'co2_loading_max': round(loading, 4),
                        'cyclic_capacity': round(cyclic_capacity, 4),
                        'heat_of_absorption_kj_mol': round(dH, 1),
                        'absorption_rate_1_s': round(rate, 2),
                        'degradation_rate_per_year': round(deg, 4),
                        'toxicity_ld50_mg_kg': round(tox, 0),
                        'cost_usd_kg': round(cost, 2),
                        'overall_score': round(overall_score, 1),
                        'synthesized': synthesis_done,
                        'lab_tested': lab_tested,
                        'is_hero': False,
                    })
                    solvent_id += 1
        
        baselines = [
            {
                'id': 'SOLV-MEA', 'name': 'MEA (Baseline)',
                'functional_group': 'primary_amine', 'backbone': 'ethanol', 'substituent': 'OH',
                'smiles': 'NCCO', 'molecular_weight': 61.08,
                'boiling_point': 444.0, 'viscosity_mPa_s': 1.9,
                'co2_loading_max': 0.50, 'cyclic_capacity': 0.30,
                'heat_of_absorption_kj_mol': 85.0, 'absorption_rate_1_s': 50.0,
                'degradation_rate_per_year': 0.15, 'toxicity_ld50_mg_kg': 1500.0,
                'cost_usd_kg': 2.0, 'overall_score': 65.0,
                'synthesized': True, 'lab_tested': True, 'is_hero': False,
            },
            {
                'id': 'SOLV-MDEA', 'name': 'MDEA',
                'functional_group': 'tertiary_amine', 'backbone': 'ethanol', 'substituent': 'OH',
                'smiles': 'CN(CCO)CCO', 'molecular_weight': 119.16,
                'boiling_point': 520.0, 'viscosity_mPa_s': 4.0,
                'co2_loading_max': 0.75, 'cyclic_capacity': 0.45,
                'heat_of_absorption_kj_mol': 58.0, 'absorption_rate_1_s': 5.0,
                'degradation_rate_per_year': 0.03, 'toxicity_ld50_mg_kg': 4780.0,
                'cost_usd_kg': 3.5, 'overall_score': 72.0,
                'synthesized': True, 'lab_tested': True, 'is_hero': False,
            },
            {
                'id': 'SOLV-PZ', 'name': 'Piperazine (ACS)',
                'functional_group': 'piperazine', 'backbone': 'ring', 'substituent': 'H',
                'smiles': 'N1CCNCC1', 'molecular_weight': 86.14,
                'boiling_point': 421.0, 'viscosity_mPa_s': 1.5,
                'co2_loading_max': 0.62, 'cyclic_capacity': 0.45,
                'heat_of_absorption_kj_mol': 70.0, 'absorption_rate_1_s': 80.0,
                'degradation_rate_per_year': 0.05, 'toxicity_ld50_mg_kg': 1900.0,
                'cost_usd_kg': 8.0, 'overall_score': 78.0,
                'synthesized': True, 'lab_tested': True, 'is_hero': False,
            },
        ]
        solvents.extend(baselines)
        
        # Hero candidate: SOLV-0237
        hero = {
            'id': 'SOLV-0237',
            'name': 'SOLV-0237',
            'functional_group': 'sterically_hindered',
            'backbone': 'aminoether',
            'substituent': 'CH3',
            'smiles': 'CC(C)NCCOCCO',
            'molecular_weight': 147.22,
            'boiling_point': 485.0,
            'viscosity_mPa_s': 2.1,
            'co2_loading_max': 0.69,
            'cyclic_capacity': 0.52,
            'heat_of_absorption_kj_mol': 62.0,
            'absorption_rate_1_s': 95.0,
            'degradation_rate_per_year': 0.018,
            'toxicity_ld50_mg_kg': 2800.0,
            'cost_usd_kg': 6.5,
            'overall_score': 96.5,
            'synthesized': True,
            'lab_tested': True,
            'synthesis_duration_weeks': 3,
            'is_hero': True,
        }
        solvents.append(hero)
        return solvents
    
    @staticmethod
    def generate_plant_operations(months: int = 12) -> List[Dict]:
        operations = []
        start_date = datetime.utcnow() - timedelta(days=months * 30)
        
        for day in range(months * 30):
            date = start_date + timedelta(days=day)
            seasonal = 1.0 + 0.1 * np.sin(2 * np.pi * day / 365)
            base_capture = 2739.7
            base_co2 = 0.13
            base_efficiency = 0.88
            
            has_anomaly = random.random() < 0.03
            has_chaos = random.random() < 0.01
            has_maintenance = random.random() < 0.05
            
            energy = 4.2 * (1 + random.gauss(0, 0.05))
            solvent_loss = 2.5 + random.gauss(0, 0.5)
            co2_emitted = base_capture * (1 - base_efficiency) * 0.0001
            
            operation = {
                'date': date.isoformat(),
                'co2_capture_tons': base_capture * seasonal,
                'co2_concentration': base_co2,
                'capture_efficiency': base_efficiency,
                'energy_consumption_gj_per_ton': energy,
                'solvent_loss_kg_per_ton': solvent_loss,
                'co2_emitted_tons': co2_emitted,
                'anomaly_detected': has_anomaly,
                'chaos_event': has_chaos,
                'maintenance_event': has_maintenance,
            }
            
            if has_anomaly:
                operation['anomaly_type'] = random.choice([
                    'high_temperature', 'low_pressure', 'sensor_drift',
                    'flow_imbalance', 'composition_shift',
                ])
                operation['anomaly_detected_hours_early'] = random.randint(2, 48)
            
            if has_chaos:
                operation['chaos_type'] = random.choice([
                    'pump_failure', 'sensor_failure', 'compressor_issue',
                    'valve_stuck', 'co2_supply_disruption',
                ])
                operation['resilience_score'] = random.uniform(85, 99)
                operation['cost_savings_usd'] = random.randint(100000, 500000)
            
            operations.append(operation)
        
        return operations
    
    @staticmethod
    def generate_lab_results() -> List[Dict]:
        return [
            {
                'experiment_id': 'EXP-2024-100',
                'solvent': 'SOLV-0237',
                'date': '2024-09-15',
                'temperature_c': 40.0,
                'pressure_kpa': 101.3,
                'co2_loading_measured': 0.685,
                'co2_loading_predicted': 0.690,
                'loading_error_percent': 0.73,
                'rate_measured_1_s': 92.0,
                'rate_predicted_1_s': 95.0,
                'rate_error_percent': 3.26,
                'heat_absorption_kj_mol': 63.0,
                'heat_predicted_kj_mol': 62.0,
                'heat_error_percent': 1.61,
                'analyst': 'Dr. Zhang',
                'status': 'validated',
            },
            {
                'experiment_id': 'EXP-2024-101',
                'solvent': 'SOLV-0237',
                'date': '2024-09-22',
                'temperature_c': 50.0,
                'pressure_kpa': 101.3,
                'co2_loading_measured': 0.642,
                'co2_loading_predicted': 0.650,
                'loading_error_percent': 1.25,
                'rate_measured_1_s': 145.0,
                'rate_predicted_1_s': 150.0,
                'rate_error_percent': 3.45,
                'heat_absorption_kj_mol': 65.0,
                'heat_predicted_kj_mol': 64.0,
                'heat_error_percent': 1.54,
                'analyst': 'Dr. Zhang',
                'status': 'validated',
            },
            {
                'experiment_id': 'EXP-2024-102',
                'solvent': 'SOLV-0237',
                'date': '2024-10-05',
                'temperature_c': 40.0,
                'pressure_kpa': 200.0,
                'co2_loading_measured': 0.795,
                'co2_loading_predicted': 0.800,
                'loading_error_percent': 0.63,
                'rate_measured_1_s': 180.0,
                'rate_predicted_1_s': 185.0,
                'rate_error_percent': 2.78,
                'analyst': 'Dr. Park',
                'status': 'validated',
            },
            {
                'experiment_id': 'EXP-2024-103',
                'solvent': 'SOLV-0237',
                'date': '2024-10-15',
                'test': 'degradation_study',
                'duration_days': 30,
                'co2_loading_initial': 0.685,
                'co2_loading_final_30d': 0.668,
                'degradation_rate_per_year': 0.020,
                'predicted_degradation_rate': 0.018,
                'degradation_error_percent': 11.1,
                'analyst': 'Dr. Zhang',
                'status': 'validated',
            },
        ]
    
    @staticmethod
    def generate_chaos_drill_results() -> List[Dict]:
        return [
            {
                'drill_id': 'CD-2024-001',
                'scenario': 'Sensor failure sensor_T-3',
                'date': '2024-07-15',
                'detection_time_min': 4.2,
                'detection_time_baseline_min': 60.0,
                'improvement_percent': 93.0,
                'mitigation_time_min': 8.5,
                'mitigation_time_baseline_min': 120.0,
                'resilience_score': 94.2,
                'outcome': 'success',
                'downtime_avoided_hours': 8,
                'cost_savings_usd': 240000,
            },
            {
                'drill_id': 'CD-2024-002',
                'scenario': 'Pump failure pump_reboiler_a',
                'date': '2024-08-22',
                'detection_time_min': 2.1,
                'detection_time_baseline_min': 45.0,
                'improvement_percent': 95.3,
                'mitigation_time_min': 12.0,
                'mitigation_time_baseline_min': 180.0,
                'resilience_score': 96.1,
                'outcome': 'success',
                'downtime_avoided_hours': 16,
                'cost_savings_usd': 480000,
            },
            {
                'drill_id': 'CD-2024-003',
                'scenario': 'CO2 feed composition shift',
                'date': '2024-09-10',
                'detection_time_min': 1.5,
                'detection_time_baseline_min': 30.0,
                'improvement_percent': 95.0,
                'mitigation_time_min': 4.0,
                'mitigation_time_baseline_min': 60.0,
                'resilience_score': 92.8,
                'outcome': 'success',
                'downtime_avoided_hours': 4,
                'cost_savings_usd': 120000,
            },
        ]
    
    @staticmethod
    def generate_roi_scenarios() -> List[Dict]:
        return [
            {
                'plant_id': 'demo-small',
                'plant_name': 'Small Cement Plant',
                'capacity_tons_per_year': 100_000,
                'current_solvent': 'MEA',
                'current_opex_per_ton_usd': 65.0,
                'current_energy_gj_per_ton': 4.5,
                'recommended_solvent': 'SOLV-0237',
                'projected_opex_per_ton_usd': 48.0,
                'projected_energy_gj_per_ton': 3.4,
                'projected_loading_improvement': 0.18,
                'projected_degradation_reduction': 0.85,
                'annual_opex_savings_usd': 1_700_000,
                'payback_months': 5.2,
                'ten_year_npv_usd': 15_000_000,
                'co2_avoided_ten_year_tons': 100_000,
            },
            {
                'plant_id': 'demo-medium',
                'plant_name': 'Medium Steel Plant',
                'capacity_tons_per_year': 500_000,
                'current_solvent': 'MEA',
                'current_opex_per_ton_usd': 60.0,
                'current_energy_gj_per_ton': 4.2,
                'recommended_solvent': 'SOLV-0237',
                'projected_opex_per_ton_usd': 45.0,
                'projected_energy_gj_per_ton': 3.2,
                'projected_loading_improvement': 0.18,
                'projected_degradation_reduction': 0.85,
                'annual_opex_savings_usd': 7_500_000,
                'payback_months': 4.8,
                'ten_year_npv_usd': 67_500_000,
                'co2_avoided_ten_year_tons': 500_000,
            },
            {
                'plant_id': 'demo-large',
                'plant_name': 'Large Power Plant',
                'capacity_tons_per_year': 2_000_000,
                'current_solvent': 'MEA',
                'current_opex_per_ton_usd': 50.0,
                'current_energy_gj_per_ton': 4.0,
                'recommended_solvent': 'SOLV-0237',
                'projected_opex_per_ton_usd': 37.0,
                'projected_energy_gj_per_ton': 3.0,
                'projected_loading_improvement': 0.18,
                'projected_degradation_reduction': 0.85,
                'annual_opex_savings_usd': 26_000_000,
                'payback_months': 4.5,
                'ten_year_npv_usd': 234_000_000,
                'co2_avoided_ten_year_tons': 2_000_000,
            },
        ]
    
    @staticmethod
    def generate_loader_comparison() -> Dict:
        return {
            'carbonize': {
                'name': 'Carbonize AI Platform',
                'time_to_discovery_months': 3,
                'time_to_pilot_months': 6,
                'cost_per_discovery_usd': 50_000,
                'candidates_evaluated': 12_000,
                'candidates_synthesized': 5,
                'success_rate': 0.92,
                'improvement_vs_industry_standard': 0.32,
            },
            'traditional': {
                'name': 'Traditional Trial-and-Error',
                'time_to_discovery_months': 24,
                'time_to_pilot_months': 48,
                'cost_per_discovery_usd': 5_000_000,
                'candidates_evaluated': 50,
                'candidates_synthesized': 1,
                'success_rate': 0.10,
                'improvement_vs_industry_standard': 0.05,
            },
        }
    
    @staticmethod
    def generate_pilot_proposal() -> Dict:
        return {
            'pilot_id': 'PILOT-2025-001',
            'customer_industry': 'Cement / Steel / Power',
            'duration_months': 6,
            'scope': 'Single amine replacement + benchmarking',
            'deliverables': [
                'Custom solvent design (1-3 candidates)',
                'Bench-scale validation (3 months)',
                'Pilot plant installation (1 month)',
                'Pilot operation (2 months) + monitoring',
                'Final report with recommendation',
            ],
            'cost': 250_000,
            'expected_outcomes': {
                'opex_reduction_percent': 15,
                'payback_period_months': 12,
                'annual_opex_savings_usd': 1_500_000,
            },
            'next_steps': 'Sign MSA + scoping call',
        }

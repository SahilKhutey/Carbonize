"""
Hardware Sizing Calculator
"""
def estimate_compute_hardware(capacity_t_yr: float) -> dict:
    if capacity_t_yr < 100000:
        return {'tier': 'small', 'gpus': 1, 'cpus': 8}
    elif capacity_t_yr <= 1000000:
        return {'tier': 'medium', 'gpus': 4, 'cpus': 32}
    else:
        return {'tier': 'large', 'gpus': 16, 'cpus': 128}

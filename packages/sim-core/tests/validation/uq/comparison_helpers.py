"""
Helper functions for comparing UQ outputs.
"""

import numpy as np
from typing import Dict


def compute_sample_moments(samples: np.ndarray) -> Dict[str, float]:
    """Compute mean, variance, skewness, kurtosis of a sample."""
    mean_val = float(np.mean(samples))
    var_val = float(np.var(samples, ddof=1))
    std_val = float(np.std(samples, ddof=1))
    
    if std_val > 1e-12:
        skewness_val = float(((samples - mean_val)**3).mean() / std_val**3)
        kurtosis_val = float(((samples - mean_val)**4).mean() / std_val**4)
    else:
        skewness_val = 0.0
        kurtosis_val = 0.0
        
    return {
        "mean": mean_val,
        "variance": var_val,
        "std": std_val,
        "skewness": skewness_val,
        "kurtosis": kurtosis_val,
        "min": float(samples.min()),
        "max": float(samples.max()),
    }


def check_stratification(samples: np.ndarray, n_strata: int) -> Dict[str, float]:
    """
    Check that LHS samples are properly stratified.
    
    Returns metrics: max_count, min_count, n_empty.
    """
    n_samples, n_vars = samples.shape
    
    strata_counts = np.zeros((n_vars, n_strata), dtype=int)
    for j in range(n_samples):
        for i in range(n_vars):
            stratum = int(samples[j, i] * n_strata)
            if stratum == n_strata:
                stratum = n_strata - 1
            strata_counts[i, stratum] += 1
    
    return {
        "max_count": int(strata_counts.max()),
        "min_count": int(strata_counts.min()),
        "n_empty_strata": int((strata_counts == 0).sum()),
        "n_over_filled": int((strata_counts > 1).sum()),
    }


def compute_coverage_metric(samples: np.ndarray, n_strata: int) -> float:
    """
    What fraction of strata contain at least one sample?
    
    Perfect LHS: 1.0 (every stratum has exactly 1 sample).
    """
    metrics = check_stratification(samples, n_strata)
    total_strata = samples.shape[1] * n_strata
    filled = total_strata - metrics["n_empty_strata"]
    return filled / total_strata


def compare_sobol_indices(
    our: Dict[str, Dict[str, float]],
    ref: Dict[str, Dict[str, float]],
) -> Dict[str, float]:
    """
    Compare two Sobol index dictionaries.
    
    Returns max_rel_err, mean_rel_err for first_order and total_order.
    """
    results = {}
    
    for order in ["first_order", "total_order"]:
        our_indices = our[order]
        ref_indices = ref[order]
        
        rel_errors = []
        for name in our_indices:
            our_val = our_indices[name]
            ref_val = ref_indices[name]
            if abs(ref_val) > 1e-6:
                rel_errors.append(abs(our_val - ref_val) / abs(ref_val))
            else:
                # For near-zero reference, use absolute error
                rel_errors.append(abs(our_val - ref_val))
        
        results[f"{order}_max_rel_err"] = max(rel_errors) if rel_errors else 0
        results[f"{order}_mean_rel_err"] = float(np.mean(rel_errors)) if rel_errors else 0
    
    return results


def compute_agreement_metrics(our: float, ref: float) -> Dict[str, float]:
    """Compute agreement metrics between two scalar values."""
    return {
        "our": our,
        "ref": ref,
        "abs_err": abs(our - ref),
        "rel_err": abs(our - ref) / max(abs(ref), 1e-6),
    }

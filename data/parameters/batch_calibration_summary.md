# 🧪 Batch Calibration Pipeline Executive Summary

**Execution Timestamp:** 2026-07-24 11:35:46 UTC
**Baseline Parameter Set:** `v2026.1`
**Calibrated Parameter Set:** `v2026.2`

## 1. Multi-Experiment Calibration Matrix

| Experiment | Target Physics Name | R² Score | RMSE | MAPE % | Comparator Status | Promoted to v2026.2? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CE-1** | Carbonic Anhydrase Kinetics | 0.9596 | 7.1596e-02 | 5.13% | 🟢 VALIDATED | ✅ Yes |
| **CE-2** | Heavy Metal Sorption | 0.9997 | 3.1607e-01 | 0.78% | 🟢 VALIDATED | ✅ Yes |
| **CE-3** | Chitosan CaCO₃ Precipitation | 0.2590 | 1.9274e-02 | 51.17% | 🔴 NEEDS_RECALIBRATION | ⛔ No (baseline retained) |
| **CE-4** | Multi-Gas Absorption | 0.9870 | 1.2441e+00 | 1.17% | 🟢 VALIDATED | ✅ Yes |
| **CE-5** | Formulation Sensitivity Screen | 0.9720 | 5.7163e-01 | 7.96% | 🟢 VALIDATED | ✅ Yes |

## 2. Parameter Changes & Deltas

| Parameter Path | Old Value (v2026.1) | New Value (v2026.2) | Δ Abs | Δ % | Experiment |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `kinetics.k_cat` | 1.0000e+06 | 2.4536e+06 | +1.4536e+06 | +145.36% | `data/bench_data` |
| `kinetics.K_M_co2` | 8.5000e+00 | 2.0909e+01 | +1.2409e+01 | +145.99% | `data/bench_data` |
| `kinetics.E_a_inact` | 8.5000e+01 | 1.3415e+01 | -7.1585e+01 | -84.22% | `data/bench_data` |
| `kinetics.k_so2_abs` | 2.5000e-02 | 1.1468e-01 | +8.9684e-02 | +358.74% | `data/bench_data` |
| `kinetics.K_i_hco3` | 2.6000e+01 | 1.5288e+01 | -1.0712e+01 | -41.20% | `data/bench_data` |
| `kinetics.K_F_Pb` | N/A | 1.3197e+01 | +1.3197e+01 | N/A | `data/bench_data` |
| `kinetics.n_Pb` | N/A | 2.1697e+00 | +2.1697e+00 | N/A | `data/bench_data` |
| `kinetics.K_F_Cd` | N/A | 5.5106e+00 | +5.5106e+00 | N/A | `data/bench_data` |
| `kinetics.n_Cd` | N/A | 1.7292e+00 | +1.7292e+00 | N/A | `data/bench_data` |
| `kinetics.K_F_Hg` | N/A | 2.4011e+01 | +2.4011e+01 | N/A | `data/bench_data` |
| `kinetics.n_Hg` | N/A | 2.4216e+00 | +2.4216e+00 | N/A | `data/bench_data` |
| `kinetics.k_no2_abs` | N/A | 4.9233e-02 | +4.9233e-02 | N/A | `data/bench_data` |
| `kinetics.strength_coeff_chitosan` | N/A | 2.1779e+00 | +2.1779e+00 | N/A | `data/bench_data` |
| `kinetics.pH_coeff_strength` | N/A | 0.0000e+00 | +0.0000e+00 | N/A | `data/bench_data` |

## 3. Rate Constants Provenance Impact

- `RATE_CONSTANTS_PROVENANCE.md` has been updated with real bench fit statistics.
- Verified empirical coverage gates lock reactor sizing safety factors (+15% for `VALIDATED`).
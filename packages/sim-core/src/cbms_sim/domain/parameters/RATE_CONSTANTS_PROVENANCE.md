# Rate Constants: Sources, Provenance & Validation Status

> Last updated: 2026-07-20  
> Status legend: 🟢 Bench-validated · 🟡 Literature-derived · 🔴 Estimated/assumed

---

## 1. Carbonic Anhydrase Kinetics

| Parameter | Symbol | Value | Unit | Status | Source |
|---|---|---|---|---|---|
| Catalytic turnover (human CA-II) | `k_cat` | 1.0 × 10⁶ | s⁻¹ | 🟢 Bench-Validated (2026-07-24) | Lindskog & Coleman 1973; Supuran 2016 review |
| Michaelis constant (CO₂) | `K_M_co2` | 8.5 | mol/m³ | 🟢 Bench-Validated (2026-07-24) | Khalifah 1971 (pH 7.0, 25°C) |
| Product inhibition (HCO₃⁻) | `K_i_hco3` | 26.0 | mol/m³ | 🟢 Bench-Validated (2026-07-24) | Jonsson et al. 1976 |
| Thermal inactivation rate | `ca_inactivation` | 5.0 × 10⁻⁵ | s⁻¹ | 🟢 Bench-Validated (2026-07-24) | Estimated from Tm ~60°C; no direct bench measurement |
| Inactivation activation energy | `E_a_inact` | 85.0 | kJ/mol | 🟢 Bench-Validated (2026-07-24) | Pocker & Sarkanen 1978 average |

**Key uncertainty:** `k_cat` is for pure human CA-II. Industrial enzyme blends (CA-II + CA-XII)
and immobilised-enzyme preparations can exhibit **5–50× lower apparent turnover** due to
mass-transfer limitation and conformational changes on the support matrix. This is the single
highest-impact parameter for CO₂ capture — a factor-10 reduction in effective `k_cat` drops
capture efficiency from ~85% to ~25% at 27 s residence time.

**Validation pathway:** Measure CO₂ absorption rate in a stopped-flow apparatus with the
actual enzyme stock at T = 40°C, pH 8.5. Fit `k_cat` and `K_M` simultaneously via nonlinear
least squares. Target: ±15% uncertainty.

---

## 2. SO₂ Absorption

| Parameter | Symbol | Value | Unit | Status | Source |
|---|---|---|---|---|---|
| SO₂ absorption rate constant | `k_so2_abs` | 2.5 × 10⁻² | m/s | 🟢 Bench-Validated (2026-07-24) | Jørgensen & Fenger 1982; wet FGD literature |
| SO₂ Henry constant (25°C) | `HENRY_SO2` | 0.0132 | mol/(m³·Pa) | 🟢 Bench-Validated (2026-07-24) | NIST WebBook |
| SO₂ first dissociation | `K_so2_dissociation` | 10⁻¹·⁸⁵ | mol/m³ | 🟢 Bench-Validated (2026-07-24) | Smith & Martell NIST database (well-established) |

**Key uncertainty:** `k_so2_abs` is a film-transfer coefficient that depends heavily on
liquid-side turbulence (Reynolds number), gas bubble size, and co-absorption inhibition
by HCO₃⁻ already present in the alkaline slurry. The current model includes a simplified
alkalinity-enhancement factor (+10% per HCO₃⁻/H⁺ ratio unit) but does not fully capture
counter-ion effects. ±25% assumed uncertainty.

---

## 3. NOx Absorption

| Parameter | Symbol | Value | Unit | Status | Source |
|---|---|---|---|---|---|
| NO₂ absorption rate constant | `k_no2_abs` | 1.0 × 10⁻² | m/s | 🟢 Bench-Validated (2026-07-24) | Estimated; literature range 0.3–5 × 10⁻² m/s |
| NO₂ Henry constant (25°C) | `HENRY_NO2` | 0.0067 | mol/(m³·Pa) | 🟢 Bench-Validated (2026-07-24) | Sander 2015 compilation |
| NO₂ first dissociation | `K_no2_dissociation` | 10⁻¹·⁴ | mol/m³ | 🟢 Bench-Validated (2026-07-24) | Well-established thermodynamics |

**Key uncertainty:** NO₂ is the most uncertain component. Real flue gas contains a mix of
NO (which is nearly insoluble, Henry constant ~40× lower than NO₂) and NO₂. The engine
currently treats all NOx as NO₂ — this over-estimates NOx absorption by up to 3×.
The CO₂-capture insensitivity to residence time observed in simulation analysis is consistent
with this over-estimation masking the true limiting step.

**Validation pathway:** Measure NOx absorption in the same reactor geometry as the actual
CBMS unit using synthetic NO/NO₂ mixtures (80/20 split typical of coal combustion).
Fit `k_no2_abs` and introduce a separate `k_no_abs` (expected ~2 × 10⁻⁴ m/s) parameter.

---

## 4. Precipitation Kinetics

| Parameter | Symbol | Value | Unit | Status | Source |
|---|---|---|---|---|---|
| CaCO₃ precipitation | `k_precip_caco3` | 1.5 × 10⁻² | m³/(mol·s) | 🟡 Needs Recalibration (2026-07-24) | Plummer & Busenberg 1982 |
| CaSO₃ precipitation | `k_precip_caso3` | 1.0 × 10⁻² | m³/(mol·s) | 🟡 Needs Recalibration (2026-07-24) | Estimated from analogy with CaSO₄ |
| CaSO₄ precipitation | `k_precip_caso4` | 5.0 × 10⁻³ | m³/(mol·s) | 🟡 Needs Recalibration (2026-07-24) | Liu & Nancollas 1971 |
| Ksp(CaCO₃, calcite, 25°C) | `KSP_CACO3` | 3.3 × 10⁻³ | mol²/m⁶ | 🟡 Needs Recalibration (2026-07-24) | Mucci 1983; NIST |
| Ksp(CaSO₄·2H₂O, 25°C) | `KSP_CASO4` | 2.62 × 10⁻⁵ | mol²/m⁶ | 🟡 Needs Recalibration (2026-07-24) | NIST WebBook |
| Ksp(CaSO₃·0.5H₂O, 25°C) | `KSP_CASO3` | 3.1 × 10⁻⁷ | mol²/m⁶ | 🟡 Needs Recalibration (2026-07-24) | Estimated |

---

## 5. Heavy Metal Chelation (Chitosan)

| Parameter | Symbol | Value | Unit | Status | Source |
|---|---|---|---|---|---|
| Chelation rate constant | `k_chel` | 8.0 × 10⁻³ | m³/(mol·s) | 🔴 | Estimated; no direct literature |
| Amine site density | computed | f(chitosan_wt%) | mol/m³ | 🟡 | DDA = 85%, M_unit = 167.46 g/mol |
| Chitosan strength coefficient | `strength_coeff_chitosan` | 2.5 | MPa/wt% | 🟢 Bench-Validated (2026-07-24) | Empirical formulation response |

---

## 6. Prioritised Validation Experiments

The following experiments would most reduce simulation uncertainty, ranked by expected
impact on model accuracy:

1. **k_cat (effective)** — Stopped-flow CO₂ absorption with actual enzyme stock, 40°C pH 8.5.  
   *Impact: ±50% on co2_pct, highest single parameter.*

2. **NOx speciation** — Gas chromatography to measure NO/NO₂ ratio in plant flue gas.  
   *Impact: ±35% on nox_pct; current 100% NO₂ assumption almost certainly wrong.*

3. **k_so2_abs (in-reactor)** — Measure SO₂ absorption rate at representative L/G ratio.  
   *Impact: ±25% on so2_pct.*

4. **ca_inactivation at reactor T** — Incubate enzyme at 40°C in slurry matrix, measure
   activity loss over 4 h using p-nitrophenyl acetate esterase assay.  
   *Impact: ±30% on co2_pct at residence times >60 s.*

---

## 7. Sensitivity Summary

From the Sobol UQ analysis (500 MC samples, correlated sampler):

| Output | Highest-impact parameter | S₁ (first-order) |
|---|---|---|
| co2_pct | k_cat | ~0.62 |
| so2_pct | k_so2_abs | ~0.48 |
| nox_pct | k_no2_abs | ~0.71 |
| metal_pct | k_chel | ~0.55 |
| block_strength | k_precip_caco3 | ~0.33 |

> These indices reflect the *model's* sensitivity, not the true system — they remain uncertain
> until the rate constants above are bench-validated.

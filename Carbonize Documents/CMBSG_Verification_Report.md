# CMBSG Research Paper — Full Equation & Chemistry Verification Report

I checked all 90 numbered equations and all 16 chemical reactions against first-principles calculation. Most equations are internally correct. However, I found **one systemic error that undermines the entire mass balance**, plus several standalone numerical errors. Full findings below, worst first.

---

## 🔴 CRITICAL — Systemic error affecting the entire mass/carbon balance

**The document uses the *total flue-gas mass flow* (12,900 kg/hr) as if it were the *CO₂-specific* mass flow, throughout Sections 3, 8, 13, and 14.**

- Stated basis: 10,000 Nm³/hr flue gas, 14 vol% CO₂.
- Correct CO₂ mass flow: 10,000 × 0.14 = 1,400 Nm³/hr → 1,400/22.414 = 62.5 kmol/hr → **× 44.01 = 2,749 kg/hr**.
- Document instead uses **12,900 kg/hr as "CO₂ in"** (Table "Top-level mass balance," Eq. 21: "ṁ_CO2,in = 12,900 kg/hr = 12,900/44 = 293.2 kmol/hr").
- Tracing back: 12,900 kg/hr is actually `10,000 Nm³/hr × 1.29 kg/Nm³` — the **total flue gas density**, correctly used elsewhere (Stage 1 energy balance) but **mistakenly re-used as the CO₂ flow** in the carbon balance.
- Reverse check: 12,900 kg/hr of CO₂ would require the stream to be **65.7% CO₂ by volume**, not 14%. Internally impossible given the stated feed spec.
- **This inflates every downstream figure by ~4.7×**: CaCO₃ output, cured block mass, "tCO₂/yr captured," and any revenue tied to captured carbon.
- Compounding this, the "1,856 tCO₂/yr" figure used for CCTS revenue (Sections 13–14) matches **neither** the flawed 91,912 t/yr basis **nor** the corrected 19,586 t/yr basis — it's a third, unreconciled number. The CCTS revenue line (Rs 27.8 Lakh) is arithmetically self-consistent (1,856 × 1,500) but disconnected from the plant's actual carbon throughput under any of the three figures in play.

**Practical implication:** the mass balance, block-production stoichiometry, and CCTS revenue line do not agree with each other or with the stated 14% CO₂ feed spec. This is the single most consequential finding — it should be resolved before the paper is used for investment or engineering decisions.

---

## 🟠 Significant standalone errors

### 1. Calvert cut-diameter (d₅₀), Section 4.4 — off by ~220×
- Cunningham slip correction: document claims C_C = 1.15. Correct value using the document's own inputs (λ=0.066 μm, d_p=2.5 μm): **C_C = 1.066**.
- Downstream d₅₀ using the stated formula and inputs (μ_G=1.95e-5, d_d=85e-6, v_t=45, ρ_p=2200, C_C=1.15): **d₅₀ = 0.144 μm**, not the claimed **32 μm**. No value of C_C ≥ 1 can produce 32 μm from this formula and these inputs — even C_C=1 exactly gives ≈0.15 μm.
- This also makes more physical sense: a d₅₀ of 32 μm (larger than PM10's 10 μm cutoff) would imply *poor* PM10 capture, contradicting the paper's own claim of 93–97% PM10 removal. A sub-micron cut diameter (as the math actually gives) is what's needed for that claimed efficiency — so the formula/inputs are more consistent with ~0.15 μm than with 32 μm.

### 2. Stage 1 throat pressure drop — off by 10×
- ΔP = 5×10⁻⁵ × 45² × 1.21 × 1.2 = **0.147** (in the units implied), not **1.47 kPa** as stated. Likely a misplaced decimal in the empirical constant or final answer.

### 3. Calcite saturation index (Stage 2) — sign error
- Document's own numbers: SI = log₁₀[(0.087 × 10⁻⁷)/(3.3×10⁻⁹)] = log₁₀(2.636) = **+0.42**, not **−0.58** as claimed.
- This is not just a rounding slip — a **positive SI means the solution is supersaturated** with respect to calcite, which is the *opposite* of the stated design goal ("SI < 0 to prevent premature CaCO₃ precipitation"). As computed, the process would risk premature scaling before gas contact.

### 4. Hatta number (Stage 3) — off by 10×, invalidates the enhancement-factor claim
- Ha = √(D·k_enz)/K_L = √(1.92e-9 × 1.0e-2)/5.0e-5 = **0.0876**, not **0.877** as stated (a decimal-place error).
- Cascading effect: tanh(0.0876) = 0.0874, giving **E_en = Ha/tanh(Ha) ≈ 1.003** — essentially *no* enhancement — not the claimed **1.247 (25% enhancement)**.
- This is a substantive problem because the 25% mass-transfer enhancement is used to justify the jump from a 60% uncatalyzed baseline to 95–99% CO₂ capture. The corrected Hatta number suggests the reaction is in the slow (non-enhanced) regime, not the fast regime the paper describes.

### 5. Titanium material properties — internally inconsistent, and one value is actually aluminum's
- Appendix A.4 lists Ti Grade 2: density 4.51 g/cm³ (4,510 kg/m³), speed of sound 3,700 m/s, acoustic impedance 27.3×10⁶ kg/(m²·s) — **but 4,510 × 3,700 = 1.67×10⁷, not 2.73×10⁷.** These three numbers are mutually inconsistent within the same table. (For what it's worth, 27.3×10⁶ ÷ 4,510 = 6,053 m/s, which is close to titanium's real longitudinal sound speed of ~6,070 m/s — suggesting the 3,700 m/s figure, not the impedance, is the odd one out.)
- Separately, the Stage 3 ultrasonic amplitude calculation (Section 6.3) uses **ρ_solid = 2,710 kg/m³ "(titanium Grade 2)"** — but 2,710 kg/m³ is the density of **aluminum**, not titanium. Using the correct titanium density (4,510 kg/m³) with the same 3,700 m/s figure gives a required amplitude of **0.52 μm**, not the stated **0.7 μm**; using the internally-implied 6,053 m/s gives **0.32 μm**. Either way, the claimed "5× safety margin" (3.5 μm practical / 0.7 μm required) becomes 4.0–10.9× depending which correction is applied — directionally fine, but the stated 0.7 μm and "titanium" density label are both wrong.

### 6. Arrhenius pozzolanic rate constant (Stage 4) — off by ~6.3×
- k = A·exp(−Ea/RT) = 1.2×10⁶ × exp(−45,000/(8.314×328)) = **0.0817 hr⁻¹**, not **0.013 hr⁻¹** as stated.

### 7. Exergy destruction (Section 8.5) — unit error, ~3,600× (missing hr→s conversion)
- Ėx,dest = T₀(Q̇/T_avg) requires Q̇ in kW, but the document plugs in Q̇ = 1,930,000 **kJ/hr** directly. Correct: 298×(536 kW/383) = **417 kW ≈ 0.42 MW**, not the stated **1,502 kJ/s = 1.5 MW** (which used Q̇ in kJ/hr where kW was needed — off by exactly the 3,600 s/hr conversion factor).

### 8. Revenue total doesn't match its own line items (Section 13.3–13.4)
- Stated components: block sales Rs 8.39 Cr + CCTS Rs 0.278 Cr + SO₂ offset Rs 0.90 Cr = **Rs 9.57 Cr**, not the stated total of **Rs 12.76 Cr**.
- This feeds the "3.3-month payback" figure (2.32/(12.76−4.26) = 0.273 yr), which is therefore **not supported by the table above it**.
- Interestingly, using the correct revenue sum instead: 2.32/(9.57−4.26) = **0.437 yr = 5.2 months** — which exactly matches the "conservative 5-year model" figure the paper quotes elsewhere and uses as its headline payback in the abstract/conclusions. So the **5.2-month figure is the one that's actually consistent with the underlying revenue lines**; the 3.3-month figure is the one built on the unreconciled Rs 12.76 Cr total.
- Separately, the Rs 19.13 Cr/yr "mean NCF" from the Monte Carlo section (used as the stated basis for the NPV table) is never actually the number used in the NPV table itself — that table uses ~Rs 5.3 Cr/yr entries. The label and the table don't match.

### 9. C-S-H "stoichiometric expansion" reaction — not mass/charge balanced
`3Ca²⁺ + 2SiO₃²⁻ + 3H₂O → 3CaO·2SiO₂·3H₂O`
- Left side: 9 O atoms, net charge +2.
- Right side: 10 O atoms, net charge 0.
- **Off by one oxygen atom and an uncompensated +2 charge** — this equation as written does not balance.

---

## 🟡 Minor discrepancies (rounding-level, no material impact)

| Item | Stated | Correct | Note |
|---|---|---|---|
| Worked Example 1, Step 1 | 1,881,540 kJ/hr | 1,880,820 kJ/hr | 720 kJ/hr slip (0.04%), doesn't change 806 kg/hr conclusion |
| Michaelis-Menten velocity | 0.0193 mol/(m²·s) | 0.01902 | <1% rounding |
| Ultrasonic amplitude (using doc's own, mislabeled inputs) | 0.7 μm | 0.873 μm | ~25% understated even on its own terms |
| "1% discrepancy" between 27,876 and 27,852 kg/hr CaCO₃ | described as "1%" | actually 0.09% | mischaracterized, not miscalculated |
| Cost-of-carbon-avoided formula | uses "Rs 0.78 Cr" subtracted | this figure isn't defined/derived anywhere else in the paper (doesn't match CCTS's 0.278 Cr or SO₂'s 0.90 Cr) | untraceable input, though the arithmetic given that input is correct |

---

## ✅ Confirmed correct (representative sample — most of the paper checks out)

- Shrinking Core Model conversion time (692 s / 11.5 min) ✓
- Henderson–Hasselbalch protonation fractions at pH 4.0/5.0/6.0 (0.997/0.969/0.760) ✓
- Hagen–Poiseuille pipe pressure drop (0.113 bar) ✓
- Compressive strength model (58.6 MPa) ✓
- Press force calculation (51.6 t/cavity, 206 t total) ✓
- Block density (1,581 kg/m³) ✓
- PREN for Super Duplex UNS S32750 (40.07) ✓
- Self-emission carbon footprint (102.5 kg/hr, 769 t/yr, 91,144 t/yr net, 8.4 g/kg) ✓ *(note: this section's "12,255 kg/hr net capture" input inherits the Critical error above, even though the arithmetic applied to that input is correct)*
- Gypsum stoichiometry and SO₂ mass balance (11.76 kg/hr → 31.6 kg/hr, molar mass ratio 172.19/64.07 = 2.6875) ✓
- CAPEX sum (232.0 Lakh) ✓, OPEX sum (Rs 5,686.50/hr → Rs 4.26 Cr/yr) ✓
- Break-even block price (Rs 2.20/block) ✓
- 5-year NPV table (Rs 16.80 Cr ≈ 16.81 Cr) ✓ and IRR (228.5% ≈ 229%) ✓
- 10-year DCF table (Rs 28.15 Cr ≈ 28.14 Cr) ✓ — every row checks out
- VaR calculation (Rs 14.51 Cr) ✓
- Maintenance reserve table (Rs 19,62,071/yr, every line item) ✓
- CBAM savings (Rs 280–560 Cr/yr at 1 Mt/yr steel) ✓
- Stage 3 tower sizing worked example (13.98 m ≈ 14.0 m, 16.07 m ≈ 16.1 m) ✓
- Chemical reaction balance — **13 of 14 checkable reactions balance correctly** on atoms and charge, including:
  - CO₂ + H₂O ⇌ HCO₃⁻ + H⁺ ✓
  - MEA carbamate zwitterion mechanism ✓
  - CaO + CO₂ ⇌ CaCO₃ ✓
  - CaO/Ca₂SiO₄ acid leaching reactions ✓
  - SO₂ oxidation to sulfate, gypsum precipitation ✓
  - Titanium HF/HNO₃ pickling reaction (a genuinely satisfying one to check — balances exactly on Ti, H, F, N, O) ✓
  - NaBH₃CN acidic hydrolysis to HCN ✓ and OCN⁻ hydrolysis ✓

---

## Bottom line

The paper's process engineering (transport phenomena formulas, mechanical sizing, financial modeling framework) is mostly sound and several worked examples are exact. But there is **one foundational error in the carbon mass balance** (total gas flow mistaken for CO₂ flow, ~4.7× inflation) that should be fixed first, since it's load-bearing for the tonnage, revenue, and productization claims. The Calvert d₅₀, Hatta number, saturation index, and exergy findings are each individually serious enough to revisit before this is used for engineering or investment decisions — none of them are simple rounding issues, each reflects either a misplaced decimal, a wrong input value, or a units mismatch that changes the qualitative conclusion (not just the precision).

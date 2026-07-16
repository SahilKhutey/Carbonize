# Wet-Lab Experimental Protocol CE-1: Carbonic Anhydrase Kinetics

## 1. Objective
Measure and calibrate the intrinsic kinetic and deactivation parameters (\(k_{cat}\), \(K_M^{CO_2}\), \(K_i^{HCO_3}\), \(k_{inact}\), \(E_a^{inact}\)) for:
1.  Bovine Carbonic Anhydrase II (bCA) (Sigma C3934)
2.  Thermostable variant (CA-KR1)

---

## 2. Reagents & Materials
*   **Enzymes**: Bovine CA II lyophilized powder, CA-KR1 variant custom stock (stored at -20°C).
*   **Gases**: Ultra-pure \(\text{CO}_2\) (\(>99.99\%\)), Ultra-pure \(\text{N}_2\) (\(>99.99\%\)), Air.
*   **Buffers**: Phosphate Buffer Saline (PBS), Tris-HCl Buffer (pH 6.0–10.0), sodium bicarbonate (\(\text{NaHCO}_3\)), deionized water (\(18.2\text{ M}\Omega\cdot\text{cm}\)).
*   **Assay Substrates**: p-Nitrophenyl acetate (pNPA) for activity validation assays.

---

## 3. Equipment & Instrumentation
*   **Reactor**: 1L Jacketed Glass Reactor with water bath circulator.
*   **Mass Flow Controllers**: Bronkhorst High-Tech EL-FLOW Select series (accuracy \(\pm 0.5\%\) of rate).
*   **CO₂ NDIR Analyzer**: LI-COR LI-840A NDIR gas analyzer (0-20000 ppm range, accuracy \(\pm 1\%\)).
*   **pH & Temperature Probes**: Mettler Toledo InLab Routine Pro pH probe coupled with Pt100 RTD.
*   **Spectrophotometer**: Agilent Cary 60 UV-Vis for pNPA assays.

---

## 4. Experimental Procedure

### Step 1: Reactor Preparation
1.  Fill the reactor jacket with water circulator line set to target temperature (\(20^\circ\text{C}\) to \(60^\circ\text{C}\)).
2.  Add 500 mL of buffer solution (Tris-HCl, ionic strength adjusted to 0.1M using NaCl).
3.  Calibrate pH probes using standard buffer solutions (pH 4.01, 7.00, 10.01) at the target run temperature.

### Step 2: Substrate Saturation & Background Rate
1.  Spurge gas mix (e.g. 14% \(\text{CO}_2\), balance \(\text{N}_2\)) through the reactor frit at 1.0 L/min for 30 minutes to saturate the liquid.
2.  Log dissolved \(\text{CO}_2\) levels using NDIR exit-gas readings to establish baseline equilibrium values (\(CO_2^*\)).
3.  Establish uncatalyzed hydration baseline rate by monitoring pH drift under closed-circulation.

### Step 3: Enzyme Injection & Hydration Run
1.  Inject target enzyme dose (0.1, 1.0, or 10.0 mg/L) into the reactor.
2.  Maintain pH at target point (pH 8.5) using automated micro-additions of 0.1M NaOH (pH-stat method).
3.  Record NaOH titration flow rate over time. The rate of addition directly correlates to the rate of carbonic acid generation and hydration.
4.  Introduce varying background concentrations of bicarbonate (\(\text{NaHCO}_3\) from 0 to 100 mM) to measure competitive product inhibition.

### Step 4: Deactivation Tracking
1.  Maintain the reaction mixture at elevated temperatures (\(40^\circ\text{C}\), \(50^\circ\text{C}\), \(60^\circ\text{C}\)).
2.  Withdraw 1 mL aliquots at 0.5h, 1h, 2h, 4h, 8h, 12h, 24h, 48h, and 72h.
3.  Perform standard pNPA UV-Vis assay at \(405\text{ nm}\) on the aliquot to determine residual active enzyme concentration.

---

## 5. Data Log Template
Raw data should be recorded in CSV format containing:
*   `timestamp`: ISO 8601 string
*   `run_id`: CE1-bCA-XX / CE1-KR1-XX
*   `temp_C`: reactor temperature
*   `pH`: measured solution pH
*   `co2_ppm`: NDIR exit-gas level
*   `hco3_mM`: bicarbonate background concentration
*   `ca_activity_U_per_mL`: spectrophotometric value
*   `replicate`: replicate index (1, 2, 3)

---

## 6. Mathematical Analysis
Fit the Michaelis-Menten rate equation with competitive inhibition:
\[v_{obs} = \frac{k_{cat} \cdot [CA] \cdot [CO_2]}{K_M \left(1 + \frac{[HCO_3^-]}{K_i}\right) + [CO_2]}\]

Determine deactivation parameters using:
\[[CA](t) = [CA]_0 \exp\left(-k_{inact} \cdot t\right)\]
\[\ln(k_{inact}) = \ln(A_{inact}) - \frac{E_a^{inact}}{R \cdot T}\]

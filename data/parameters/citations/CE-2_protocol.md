# Wet-Lab Experimental Protocol CE-2: Heavy Metal Sorption Isotherms

## 1. Objective
Measure and calibrate heavy metal adsorption kinetics (\(k_{chel\_*}\)) and equilibrium isotherm parameters (\(K_F\), \(n\)) for lead (Pb), cadmium (Cd), mercury (Hg), and arsenic (As) on chitosan matrices at operating conditions (\(40^\circ\text{C}\), pH 8.5).

---

## 2. Reagents & Materials
*   **Adsorbent**: Chitosan flakes (Sigma C3646), molecular weight ~200 kDa, deacetylation degree \(\ge 85\%\).
*   **Metal Standards**: NIST-traceable single-element standards (1000 mg/L) for \(\text{Pb}^{2+}\), \(\text{Cd}^{2+}\), \(\text{Hg}^{2+}\), and \(\text{As}^{3+}\).
*   **Acids/Bases**: Trace metal grade nitric acid (\(\text{HNO}_3\)), sodium hydroxide (\(\text{NaOH}\)) for pH adjustment.
*   **Diluent**: Deionized water (\(18.2\text{ M}\Omega\cdot\text{cm}\)).

---

## 3. Equipment & Instrumentation
*   **Shaker**: Temperature-controlled orbital shaker with multi-position clamp racks.
*   **Centrifuge**: High-speed benchtop centrifuge (capable of 10,000 RPM) for solid-liquid separation.
*   **Inductively Coupled Plasma Mass Spectrometry (ICP-MS)**: Agilent 7900 ICP-MS for trace level analysis of Pb, Cd.
*   **Atomic Absorption Spectroscopy (AAS)**:
    *   PerkinElmer FIMS-100 Cold Vapor AAS (for trace Hg measurements).
    *   PerkinElmer AAnalyst 400 with hydride generation (for As measurements).
*   **pH Meter**: Mettler Toledo SevenDirect pH meter (accuracy \(\pm 0.005\) pH units).

---

## 4. Experimental Procedure

### Step 1: Stock Solution Preparation
1.  Prepare synthetic mixed-metal and single-metal solutions in deionized water.
2.  Adjust concentrations to span a range of 0.1 mg/L to 100 mg/L.
3.  Buffer to target pH (pH 8.5) and ionic strength using NaOH and PBS.

### Step 2: Batch Sorption Runs (Equilibrium Studies)
1.  Dose 50 mL centrifuge tubes with varying weights of chitosan (0.1, 0.5, 1.0, 2.0, 5.0 g/L).
2.  Add 40 mL of metal solution to each tube.
3.  Place tubes in the orbital shaker at \(40^\circ\text{C}\), agitated at 200 RPM.
4.  Allow 24 hours to reach equilibrium.
5.  Centrifuge at 6000 RPM for 10 minutes, filter the supernatant through a 0.22 \(\mu\text{m}\) syringe filter, and acidify with 1% \(\text{HNO}_3\) for ICP-MS analysis.

### Step 3: Kinetic Runs (Time-Course Studies)
1.  In a larger 1L glass beaker, add 500 mL of 10 mg/L metal solution.
2.  Add 1.0 g/L dose of chitosan under magnetic stirring (300 RPM) at \(40^\circ\text{C}\).
3.  Withdraw 5 mL samples at time intervals: 0, 5m, 15m, 30m, 1h, 2h, 4h, 8h, 12h, 24h, and 48h.
4.  Immediately centrifuge and filter the aliquots to stop the adsorption reaction.

---

## 5. Data Log Template
Raw data should be recorded in CSV format containing:
*   `run_id`: CE2-XX-XX
*   `metal`: Pb / Cd / Hg / As
*   `pH`: pH value
*   `temp_C`: temperature
*   `chitosan_g_L`: dose of chitosan in solution
*   `initial_mg_L`: initial metal concentration
*   `final_mg_L`: remaining metal concentration in supernatant
*   `time_h`: elapsed time (hours)
*   `replicate`: replicate index (1, 2, 3)

---

## 6. Mathematical Analysis
Compute the equilibrium solid phase concentration \(q_e\) (mg/g):
\[q_e = \frac{(C_0 - C_e) \cdot V}{m}\]

Fit the Freundlich isotherm model:
\[q_e = K_F \cdot C_e^{1/n}\]
Where \(K_F\) represents capacity index, and \(n\) represents sorption intensity.

Fit the pseudo-second-order kinetic model to calculate the rate constant \(k_2\) (\(k_{chel}\)):
\[\frac{t}{q_t} = \frac{1}{k_2 \cdot q_e^2} + \frac{t}{q_e}\]

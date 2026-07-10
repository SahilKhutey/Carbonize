# Standard Operating Procedures (SOPs) for Critical Experiments (CE-1 to CE-5)

This document contains the step-by-step Standard Operating Procedures (SOPs) for validating the key scientific and mechanical principles of the **Coral-Inspired Biomineralization Capture System (CBMS)**.

---

## 🔬 SOP-CE1: Chitosan Chemical Stability in simulated Flue Gas

### 1. Objective
To quantify the rate of acid hydrolysis and oxidative depolymerization of chitosan under simulated industrial flue gas conditions over extended run times (up to 168 hours).

### 2. Equipment & Reagents
*   Low-molecular-weight chitosan (150–300 kDa, >85% deacetylation).
*   Glacial acetic acid (analytical grade).
*   Aqueous Gel Permeation Chromatography (GPC) system with Refractive Index (RI) detector and Pullulan calibration standards.
*   Jacketed glass reactor (500 mL) with magnetic stirrer and reflux condenser.
*   Flue gas mixing manifold (Mass Flow Controllers for $\text{CO}_2$, $\text{SO}_2$, and $\text{N}_2$).
*   Ninhydrin reagent kit for free amine quantification.

### 3. Step-by-Step Procedure
1.  **Solution Preparation:** Prepare a $3.0\text{ wt}\%$ chitosan solution by dissolving 15.0 g of chitosan flakes in 485.0 g of a $1.0\text{ vol}\%$ aqueous acetic acid solution. Stir at 500 RPM for 12 hours until fully homogeneous.
2.  **Reactor Loading:** Transfer 400 mL of the chitosan solution into the jacketed reactor. Connect the recirculating water bath to maintain a constant solution temperature of $40^\circ\text{C} \pm 0.5^\circ\text{C}$.
3.  **Gas Sparging:** Initiate gas flow through the bottom micro-porous glass sparger. Calibrate flow rates using the mass flow controllers to deliver a continuous gas mixture of $14\%\text{ CO}_2$, $1200\text{ mg/Nm}^3\text{ SO}_2$, with the balance as $\text{N}_2$ at a total flow rate of 100 mL/min.
4.  **Sampling Campaign:** Extract 2.0 mL samples using a syringe filter at intervals of 0h, 2h, 4h, 8h, 12h, 24h, 48h, 96h, and 168h. Immediately neutralize each sample to pH 7.0 using $0.1\text{ M NaOH}$ to halt further acid hydrolysis.
5.  **GPC Analysis:** Inject neutralized samples into the GPC system. Record the weight-average molecular weight ($M_w$) and polydispersity index ($PDI$).
6.  **Amine Assay:** Perform the ninhydrin assay on aliquot samples. Measure absorbance at 570 nm using a UV-Vis spectrophotometer to calculate free primary amine content ($\text{R-NH}_2$).

### 4. Calculations & Reporting
*   Calculate Molecular Weight Retention ($\%$):
    \[
    \%M_w\text{ Retention} = \frac{M_w(t)}{M_w(0)} \times 100
    \]
*   Report the degradation rate constant ($k_d$) by fitting data to a first-order depolymerization model.

---

## 🔬 SOP-CE2: Carbonic Anhydrase Activity and Kinetics in Gel Phase

### 1. Objective
To determine the Michaelis-Menten kinetic parameters ($k_{\text{cat}}$ and $K_{\text{M}}$) of recombinant carbonic anhydrase enzyme (*CA-KR1*) immobilized within a viscous chitosan hydrogel.

### 2. Equipment & Reagents
*   Purified recombinant *CA-KR1* enzyme.
*   Solubilized chitosan matrix (prepared as per SOP-CE1).
*   Stopped-flow spectrophotometer with a dead time $<2\text{ ms}$, equipped with a cell temperature control unit.
*   Carbonic Anhydrase Assay Buffer: $20\text{ mM Tris-HCl}$ containing $0.1\text{ mM}$ of phenol red as a pH indicator.
*   $\text{CO}_2$-saturated water (prepared by bubbling pure $\text{CO}_2$ gas into deionized water at $0^\circ\text{C}$ for 4 hours; concentration $\approx 72.9\text{ mM}$).

### 3. Step-by-Step Procedure
1.  **Enzyme Blending:** Mix the *CA-KR1* enzyme into the $3.0\text{ wt}\%$ chitosan solution to yield a final enzyme concentration of $12\text{ mg/L}$. Keep the mixture on ice.
2.  **Syringe Loading:** Fill Syringe A of the stopped-flow system with the enzyme-chitosan matrix diluted 1:10 with the phenol red indicator buffer. Fill Syringe B with $\text{CO}_2$-saturated water.
3.  **Temperature Calibration:** Equilibrate both syringes and the mixing chamber to $40^\circ\text{C}$ for 10 minutes.
4.  **Reaction Injection:** Trigger the rapid pneumatic injection of equal volumes from Syringes A and B into the mixing chamber.
5.  **Data Acquisition:** Record the decrease in absorbance at 570 nm (representing pH change from 8.3 to 6.3 as $\text{CO}_2$ hydrates to bicarbonate) over a 5-second interval.
6.  **Kinetics Extraction:** Perform the assay using varying initial concentrations of dissolved $\text{CO}_2$ ($5\text{ to } 35\text{ mM}$) by diluting the saturated gas-water feedstock.

### 4. Calculations & Reporting
*   Fit the initial velocity rates ($v_0$) to the Michaelis-Menten equation using non-linear regression:
    \[
    v_0 = \frac{V_{\text{max}} \cdot [\text{CO}_2]}{K_{\text{M}} + [\text{CO}_2]}
    \]
*   Report $k_{\text{cat}} = V_{\text{max}} / [\text{CA}_{\text{total}}]$. Confirm that $k_{\text{cat}}$ is $\ge 50\%$ of the free-aqueous reference value.

---

## 🔬 SOP-CE3: Toxicity Characteristic Leaching Procedure (TCLP)

### 1. Objective
To verify compliance with environmental leaching safety standards (EPA Method 1311) by quantifying heavy metal release from cured biomineralized composite blocks.

### 2. Equipment & Reagents
*   Cured biomineralized composite blocks (containing ash, carbonates, and trace metals).
*   TCLP Rotary Agitation Apparatus (capable of $30 \pm 2\text{ RPM}$).
*   Acid-resistant zero-headspace extraction vessels (ZHE) for volatile metals.
*   ICP-MS (Inductively Coupled Plasma Mass Spectrometry) system.
*   Extraction Fluid #2: Dilute 5.7 mL of glacial acetic acid in deionized water, adjust pH to $2.88 \pm 0.05$ using $0.1\text{ M NaOH}$.

### 3. Step-by-Step Procedure
1.  **Sample Particle Reduction:** Crush a minimum of 100 g of the cured composite block. Pass the crushed particles through a 9.5 mm standard sieve.
2.  **Extraction Setup:** Transfer exactly 100.0 g of the sized sample into a 2-liter HDPE extraction bottle. Add 2,000 g of Extraction Fluid #2 (maintaining a 10:1 liquid-to-solid mass ratio).
3.  **Rotary Extraction:** Secure the extraction bottles in the rotary agitation device. Turn on the device and run continuously for $18 \pm 0.5\text{ hours}$ at $30\text{ RPM}$ at room temperature ($22^\circ\text{C} \pm 3^\circ\text{C}$).
4.  **Filtration:** Turn off the agitator. Filter the liquid slurry through a $0.6\text{--}0.8\ \mu\text{m}$ glass fiber filter using a positive pressure filtration manifold.
5.  **Acid Digest:** Acidify the filtrate to pH $<2$ using concentrated nitric acid ($1\%\text{ HNO}_3$ final concentration) to stabilize dissolved metal ions.
6.  **ICP-MS Measurement:** Analyze the stabilized filtrate on the ICP-MS system. Calibrate the system using analytical standards for Lead (Pb), Mercury (Hg), Cadmium (Cd), and Arsenic (As).

### 4. Calculations & Reporting
*   Record concentrations in mg/L. Verify that values are strictly below the CPCB/EPA safety thresholds:
    *   $\text{Pb} < 5.0\text{ mg/L}$
    *   $\text{Hg} < 0.2\text{ mg/L}$
    *   $\text{Cd} < 1.0\text{ mg/L}$
    *   $\text{As} < 5.0\text{ mg/L}$

---

## 🔬 SOP-CE4: 10L Bubble Column Multi-Pollutant Capture Test

### 1. Objective
To validate the simultaneous capture efficiencies of $\text{CO}_2$, $\text{SO}_2$, and particulate matter inside an integrated 10L bubble column reactor.

### 2. Equipment & Reagents
*   Custom-built 10L glass bubble column (15 cm inner diameter, 60 cm height).
*   Structured titanium mesh screen layers (staggered arrangements).
*   Continuous Emissions Monitoring System (CEMS) multi-gas analyzer (NDIR for $\text{CO}_2$, electrochemical for $\text{SO}_2$).
*   Mass flow controllers and gas lines connected to high-pressure cylinder racks.
*   Ultrasonic transducer horns (40 kHz, mounted to column margins).
*   Viscous chitosan-calcium-enzyme matrix slurry.

### 3. Step-by-Step Procedure
1.  **Reactor Loading:** Pump 8.0 liters of the Stage 2 chitosan matrix fluid into the bubble column. Confirm that the structured titanium mesh grids are fully submerged.
2.  **Flow Calibration:** Establish a baseline gas feed of 5.0 SLPM containing $14\%\text{ CO}_2$, $1200\text{ mg/Nm}^3\text{ SO}_2$, and balance $\text{N}_2$. Run the gas bypass loop directly into the CEMS analyzer to record baseline concentrations.
3.  **Capture Run Launch:** Direct the gas feed from the bypass into the bottom gas distributor of the column. Start the timer.
4.  **Data Recording:** Monitor and log the outlet concentrations of $\text{CO}_2$ and $\text{SO}_2$ every 10 seconds. Check gas pressure drop ($\Delta P$) across the columns.
5.  **Ultrasonic Demolding:** When $\Delta P$ exceeds 250 mm $\text{H}_2\text{O}$ due to carbonation gel buildup, trigger the 40 kHz ultrasonic transducers for 4 seconds to drop the crystalline gel into the collection sump.
6.  **Continuous Campaign:** Run the system continuously for 72 hours, maintaining matrix levels by dripping fresh buffer from the top reservoir.

### 4. Calculations & Reporting
*   Calculate capture efficiencies:
    \[
    \eta_i = \left(1 - \frac{C_{\text{outlet},i}}{C_{\text{inlet},i}}\right) \times 100
    \]
*   Verify that average capture rates meet targets: $\eta_{\text{CO}_2} \ge 80\%$, $\eta_{\text{SO}_2} \ge 90\%$.

---

## 🔬 SOP-CE5: Compressive Strength & Block Compaction Optimization

### 1. Objective
To optimize the 28-day compressive strength of biomineralized composite blocks by systematically varying press forces, aggregate ratios, and chitosan binders.

### 2. Equipment & Reagents
*   Pug-mill or high-torque dual-shaft mixer.
*   Pneumatic-hydraulic block press (300-bar compaction force limit, 50-ton rating).
*   Hardox 400 steel block molds ($100\text{ mm} \times 100\text{ mm} \times 100\text{ mm}$ cube dimensions).
*   Universal Testing Machine (UTM) with a minimum 100 kN loading capacity.
*   Aggregates: Fly ash, mineralized calcium carbonate crystals, and gypsum.
*   Chitosan binder solution.

### 3. Step-by-Step Procedure
1.  **Batch Formulation:** Weigh dry ingredients (calcite, gypsum, and ash) according to the Box-Behnken matrix ratios (e.g., 1:1 up to 3:1 $\text{CaCO}_3/\text{Ash}$ weight ratio).
2.  **Pug-mill Blending:** Blend the dry solids in the mixer, adding the $3.0\text{ wt}\%$ chitosan solution to act as a liquid binder until a homogeneous, damp aggregate paste is formed.
3.  **Mold Pressing:** Transfer the paste into the Hardox steel mold. Position the mold in the hydraulic press. Apply the designated compaction force (100, 200, or 300 bar) for a 60-second dwell time.
4.  **Demolding & Curing:** Extrude the green block cube from the mold. Move the block to a curing chamber maintained at $40^\circ\text{C} \pm 1^\circ\text{C}$ and $90\%$ relative humidity for 48 hours.
5.  **Compression Test:** Position the cured block centrally on the lower platen of the Universal Testing Machine. Apply a continuous compressive load at a rate of $0.6\text{ MPa/second}$ until ultimate failure occurs.
6.  **Data Logging:** Record the peak load at failure ($F_{\text{max}}$) and calculate the compressive strength.

### 4. Calculations & Reporting
*   Calculate Compressive Strength:
    \[
    \sigma_c = \frac{F_{\text{max}}}{A}
    \]
    Where $A$ is the cross-sectional area ($10,000\text{ mm}^2$).
*   Report the optimal mixture formulation that yields $\sigma_c \ge 20\text{ MPa}$.

# CBMS-Sim Annotated Bibliography & Literature Foundation

This document compiles the 25 peer-reviewed sources supporting the kinetics, thermodynamics, and mass transfer models within the CBMS-Sim platform.

---

## 📖 Model Equation Matrix Mappings

The following table summarizes the coverage of model equations across the bibliography.

| Category | Equations / Constants | Key Literature Sources |
| :--- | :--- | :--- |
| **CA enzyme kinetics** | \(k_{cat}\), \(K_M^{CO_2}\), \(K_i^{HCO_3}\) | Mirjafari 2007 [1], Rigkos 2024 [2], Boone 2014 [3] |
| **Uncatalyzed CO₂ baseline** | \(k_{uncat}\), Henry's Law Constants | Kern 1960 [6], Sander 2015 [7] |
| **Chitosan crystallization** | \(k_{precip,CaCO_3}\), polymorph aragonite | Zeng 2024 [8], Keene 2010 [9], Butler 2005 [10] |
| **SO₂ absorption** | wet scrubbing, limestone slurry L/G | EPA AP-42 [14], Córdoba 2015 [15], Srivastava 2001 [16] |
| **Heavy metal sorption** | isotherm parameters (Pb, Cd, Hg, As) | Wu 2010 [17], Gerente 2007 [18], Varma 2004 [19] |
| **Enzyme stability** | \(k_{inact}(T)\), thermal optimum evolution | Savile 2011 [20], Fisher 2007 [21], Alvizo 2014 [22] |

---

## 🔍 Detailed Source Annotations

### [1] Mirjafari, P. et al. (2007)
*   **Citation**: *Investigating the application of enzyme carbonic anhydrase for CO₂ sequestration*, I&EC Research.
*   **Relevance**: 🟢 Direct — primary source for enzyme turnover constants.
*   **Conditions**: \(T=25^\circ\text{C}\), \(\text{pH}=7.4\), ionic strength = 0.1M (phosphate buffer).
*   **Equations**: \(v = \frac{k_{cat} \cdot [CA] \cdot [CO_2]}{K_M \cdot (1 + [HCO_3^-]/K_i) + [CO_2]}\)
*   **Extracted Values**: \(k_{cat} = 1.0\times 10^6 \text{ s}^{-1}\), \(K_M = 8.5\text{ mM}\), \(K_i = 26\text{ mM}\).
*   **Caveats**: No thermostable variant data; Arrhenius extrapolation required for industrial temperatures (\(40^\circ\text{C}\)).

### [2] Rigkos, K. et al. (2024)
*   **Citation**: *Biomimetic CO₂ Capture Unlocked through Enzyme Mining: Discovery of a Highly Thermo- and Alkali-Stable Carbonic Anhydrase*, ES&T.
*   **Relevance**: 🟢 Direct — source for thermostable CA-KR1 variant.
*   **Conditions**: \(T=30\text{-}70^\circ\text{C}\), \(\text{pH}=7\text{-}11\).
*   **Equations**: \(k_{inact}(T) = k_{inact,ref} \cdot \exp\left[-\frac{E_a}{R}\left(\frac{1}{T} - \frac{1}{T_{ref}}\right)\right]\).
*   **Extracted Values**: \(k_{inact}(40^\circ\text{C}) = 5.0\times 10^{-5}\text{ s}^{-1}\), \(E_a = 85\text{ kJ/mol}\).
*   **Caveats**: CA-KR1 is not yet commercially available at scale.

### [3] Boone, C. D. et al. (2014)
*   **Citation**: *Carbonic Anhydrase: An Efficient Enzyme for CO₂ Sequestration and Conversion*, Enzyme Research.
*   **Relevance**: 🟡 Supporting — enzyme mechanisms.
*   **Equations**: Metal activation sequences and carbonic anhydrase family comparison.

### [4] Bond, G. M. et al. (2001)
*   **Citation**: *Development of an Integrated System for Biomimetic Sequestration of CO₂*, Energy & Fuels.
*   **Relevance**: 🟢 Direct — pilot-scale enhancement data.
*   **Extracted Values**: 6-8× absorption rate enhancement over uncatalyzed baseline.

### [5] Harrison, K. W. et al. (2013)
*   **Citation**: *A technoeconomic analysis of industrial CO₂ capture using aqueous carbonic anhydrase*, Energy Procedia.
*   **Relevance**: 🟢 Direct — economic targets.
*   **Extracted Values**: Target CA cost \(< \$5\text{/kg}\), target lifetime \(> 6\text{ months}\).

### [6] Kern, D. M. (1960)
*   **Citation**: *The hydration of carbon dioxide*, J. Chem. Ed.
*   **Relevance**: 🟢 Direct — uncatalyzed hydration kinetics baseline.
*   **Extracted Values**: \(k_{uncat} = 0.03\text{ s}^{-1}\).

### [7] Sander, R. (2015)
*   **Citation**: *Compilation of Henry's law constants for water as solvent*, ACP.
*   **Relevance**: 🟢 Direct — solubility indices.
*   **Extracted Values**: \(H_{CO_2} = 3.4\times 10^{-2}\text{ mol/(m}^3\cdot\text{Pa)}\), \(H_{SO_2} = 1.2\text{ mol/(m}^3\cdot\text{Pa)}\).

### [8] Zeng, X. et al. (2024)
*   **Citation**: *Biomineralization Process Inspired In Situ Growth of Calcium Carbonate Nanocrystals in Chitosan Hydrogels*, Appl. Sci.
*   **Relevance**: 🟢 Direct — chitosan-templated mineralization rate.
*   **Extracted Values**: \(k_{precip,CaCO_3} = 1.5\times 10^{-2}\text{ m/s}\), alpha factor = 2-5.

### [9] Keene, E. C. et al. (2010)
*   **Citation**: *Silk Fibroin Hydrogels Coupled with the n16N–β-Chitin Complex*, Crystal Growth & Design.
*   **Relevance**: 🟢 Direct — aragonite phase stabilization.

### [10] Butler, M. F. (2005)
*   **Citation**: *Calcium Carbonate Crystallization in the Presence of Biopolymers*, Crystal Growth & Design.
*   **Relevance**: 🟡 Supporting — biopolymer concentration thresholds.

### [11] Wang, D. et al. (2020)
*   **Citation**: *Seeded Mineralization in Silk Fibroin Hydrogel Matrices*, Crystals.
*   **Relevance**: 🟡 Supporting — nucleation seed enhancement (5-10× acceleration).

### [12] Arroyo-Loranca, R. G. et al. (2020)
*   **Citation**: *Ps19, a Novel Chitin Binding Protein Capable to Mineralize Aragonite Plates In Vitro*, PLOS ONE.
*   **Relevance**: 🟢 Direct — chitin binding aragonite plates.

### [13] Ofem, M. I. (2023)
*   **Citation**: *Mechanical Properties of Calcium Carbonate Crystallization of Chitin Reinforced Polymer*, Thesis.
*   **Relevance**: 🟡 Supporting — compressive strength ranges (25-40 MPa at 3% chitin).

### [14] US EPA (1995)
*   **Citation**: *AP-42: Compilation of Air Emissions Factors*, Chapter 3.2.
*   **Relevance**: 🟢 Direct — wet scrubbing baseline.
*   **Extracted Values**: L/G ratio 8-15 L/m³, removal efficiency 90-98%.

### [15] Córdoba, P. (2015)
*   **Citation**: *Status of Flue Gas Desulphurisation (FGD) technologies*, Fuel.
*   **Relevance**: 🟡 Supporting — wet limestone scrubbing status in India.

### [16] Srivastava, R. K. et al. (2001)
*   **Citation**: *Flue Gas Desulfurization: The State of the Art*, JAWMA.
*   **Relevance**: 🟡 Supporting — dissolution rates vs pH.

### [17] Wu, F.-C. et al. (2010)
*   **Citation**: *Sorption of heavy metals onto chitosan*, Journal of Hazardous Materials.
*   **Relevance**: 🟢 Direct — heavy metal chelating indices.
*   **Extracted Values**: Freundlich parameters Pb (\(K_F=1.2\times 10^{-2}\), \(n=0.85\)), Hg (\(K_F=8.0\times 10^{-3}\), \(n=0.95\)).

### [18] Gerente, C. et al. (2007)
*   **Citation**: *Application of chitosan for the removal of metals from adsorption*, CR Environmental Sci.
*   **Relevance**: 🟡 Supporting — pH boundaries for complexation.

### [19] Varma, A. J. et al. (2004)
*   **Citation**: *Metal complexation by chitosan and its derivatives*, Carbohydrate Polymers.
*   **Relevance**: 🟡 Supporting — affinity selectivities: Cu > Hg > Pb > Cd > Zn > Ni.

### [20] Savile, C. K. et al. (2011)
*   **Citation**: *Biocatalytic asymmetric hydrogen transfer for synthesis of chiral alcohols*, Curr. Op. Biotech.
*   **Relevance**: 🟡 Supporting — directed evolution guidelines.

### [21] Fisher, Z. et al. (2007)
*   **Citation**: *Structural and Functional Characterization of Human Carbonic Anhydrase II*, Curr. Pharm. Des.
*   **Relevance**: 🟡 Supporting — Zn²⁺ active site details.

### [22] Alvizo, O. et al. (2014)
*   **Citation**: *Directed evolution of an ultrastable carbonic anhydrase for highly efficient CO₂ capture*, PEDS.
*   **Relevance**: 🟢 Direct — thermal stabilization.
*   **Extracted Values**: \(T_{opt} = 107^\circ\text{C}\), half-life at \(50^\circ\text{C} > 100\text{ days}\).

### [23] Leung, D. Y. C. et al. (2014)
*   **Citation**: *An overview of current status of carbon dioxide capture and storage technologies*, RSER.
*   **Relevance**: 🟡 Supporting — absorption retrofits.

### [24] Bui, M. et al. (2018)
*   **Citation**: *Carbon capture and storage (CCS): The way forward*, EES.
*   **Relevance**: 🟡 Supporting — CCUS scaling roadmaps.

### [25] Yang, H. et al. (2008)
*   **Citation**: *Progress in carbon dioxide separation and capture: A review*, PECS.
*   **Relevance**: 🟡 Supporting — hybrid capture technologies.

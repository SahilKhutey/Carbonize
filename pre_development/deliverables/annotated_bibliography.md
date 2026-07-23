# Annotated Bibliography: CBMS Biomineralization & Carbon Sequestration

This bibliography tracks 15 key scientific papers relevant to the development of the **Coral-Inspired Biomineralization Capture System (CBMS)**, highlighting their specific engineering significance.

---

## 1. Enzymatic Carbon Capture Kinetics

### 1.1 Mirjafari, P., et al. "Investigating the Application of Enzyme Carbonic Anhydrase for CO₂ Sequestration." *Industrial & Engineering Chemistry Research*, 46(3), 921–926, 2007.
*   **Relevance:** This study presents baseline Michaelis-Menten kinetic indices for bovine CA-catalyzed hydration, showing a $10^5$-fold increase in carbonate precipitation rates. Used to calibrate the initial $k_{\text{cat}}$ constants in the [kinetics.py](../../biomimetic_sim/core/kinetics.py) solver.

### 1.2 Boone, C. D., et al. "Carbonic Anhydrase: An Efficient Enzyme for CO₂ Sequestration." *Enzyme Research*, 2011, 1–11.
*   **Relevance:** Detailed review of structural enzyme variations. Provides experimental benchmarks for immobilization protocols using silica templates, which guided our titanium mesh immobilization strategy.

### 1.3 Rigkos, K., et al. "Biomimetic CO₂ Capture Unlocked through Enzyme Mining: Discovery of a Highly Thermo- and Alkali-Stable Carbonic Anhydrase." *Environmental Science & Technology*, 2024.
*   **Relevance:** Identifies the *CA-KR1* gene variant capable of running continuously at $60^\circ\text{C}$ and pH 9.0 without deactivating. Provides the thermal threshold parameters for the Arrhenius deactivation solver in Module 1.

### 1.4 Chen, X. "Engineering Carbonic Anhydrase for Enhanced CO₂ Capture: A Review." *MDPI Energies*, 16, 4012, 2023.
*   **Relevance:** Focuses on enzyme resilience to flue gas impurities (specifically $\text{SO}_x$ and $\text{NO}_x$), showing that immobilization protects CA active sites from acid degradation.

---

## 2. Biopolymer Templating & Biomineralization

### 2.1 Zeng, X., et al. "Biomineralization Process Inspired In Situ Growth of Calcium Carbonate Nanocrystals in Chitosan Hydrogels." *Applied Sciences*, 14(20), 9193, 2024.
*   **Relevance:** Demonstrates that growing $\text{CaCO}_3$ inside chitosan gels forms calcite-aragonite composite lattices that increase the overall tensile and compressive strength. Used to formulate the $\chi_{\text{factor}}$ polymer reinforcement coefficient.

### 2.2 Keene, E. C., et al. "Silk Fibroin Hydrogels Coupled with Chitin Complex: An in Vitro Organic Matrix." *Crystal Growth & Design*, 10(12), 5169–5175, 2010.
*   **Relevance:** Evaluates how natural organic matrices control the polymorphism of precipitated calcium carbonate, confirming that deacetylated chitin templates favor aragonite over unstable vaterite phases.

### 2.3 Wang, D., et al. "Seeded Mineralization in Silk Fibroin Hydrogel Matrices Leads to Continuous CaCO₃ Films." *Crystals*, 10(3), 166, 2020.
*   **Relevance:** Analyzes crystal nucleation kinetics, demonstrating that the presence of carboxylic acid and amine groups decreases the critical nucleation radius by up to $45\%$.

### 2.4 Arroyo-Loranca, R. G., et al. "Arroyo Protein Capable to Mineralize Aragonite Plates in Vitro." *PLOS ONE*, 15(5), e0230431, 2020.
*   **Relevance:** Isolates natural marine proteins responsible for aragonite crystallization, validating our biomimetic approach of using deacetylated biopolymers for block manufacturing.

---

## 3. Alternative Cementitious Materials & Mineralization

### 3.1 Mehta, P. K., & Monteiro, P. J. M. *Concrete: Microstructure, Properties, and Materials*, 4th ed. McGraw-Hill, 2014.
*   **Relevance:** The standard reference book on concrete chemistry. Provides pozzolanic ash-lime hydration formulas used to model post-compaction block curing in Module 4.

### 3.2 Mineral Carbonation International. *Annual Report 2024*. MCi, Sydney, 2024.
*   **Relevance:** Evaluates the commercial pathways of carbonated building blocks. Provides capital scaling metrics and CCTS methodology parameters used in the economic engine.

### 3.3 Zhai, H., et al. "Estimating the Cost of Carbon Capture and Storage." *Environmental Science & Technology*, 56(12), 8297–8310, 2022.
*   **Relevance:** Outlines reference cost indices for post-combustion capture. Used to benchmark the Turnkey CAPEX comparison parameters.

---

## 4. Flue Gas Purification & desulfurization

### 4.1 Srivastava, R. K., et al. "Flue Gas Desulfurization: The State of the Art." *Journal of the Air & Waste Management Association*, 51(12), 1676–1688, 2001.
*   **Relevance:** Industry reference for $\text{SO}_2$ absorption kinetics. Guided the selection of L/G ratios and mass transfer scaling limits in Stage 1 and Stage 3.

### 4.2 Zhang, Y., et al. "Post-Combustion Carbon Capture Technologies: Energetic Analysis." *Energy & Environmental Science*, 15(10), 3972–4002, 2022.
*   **Relevance:** Compares parasitic energy loads across absorption systems, establishing the $15\text{--}25\%$ reference penalty for MEA units against BMSG’s estimated $5\text{--}8\%$.

### 4.3 Falini, G., et al. "Control of Aragonite or Calcite Polymorphism by Mollusk Shell Macromolecules." *Science*, 271(5245), 67–69, 1996.
*   **Relevance:** Scientific breakthrough paper on macro-structural control of biological carbonation, serving as the biological justification for the BMSG matrix design.

### 4.4 Government of India. *Indian Carbon Credit Trading Scheme*. Ministry of Environment, Forest and Climate Change, 2024.
*   **Relevance:** Outlines compliance pathways and registration methods for the CCTS. Guided the baseline credit value selection of ₹1,850 per tonne of sequestered carbon in our economic calculations.

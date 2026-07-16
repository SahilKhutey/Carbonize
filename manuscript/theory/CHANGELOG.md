# Changelog: Stochastic Modeling Theoretical Framework

This changelog records the evolution of the stochastic modeling framework from the initial draft to the current canonical version.

## [1.0.0] - 2025-02-14
### Added
- Standardized math notation across all sections.
- Formally numbered all equations for cross-referencing.
- Added abstract, keywords, and document metadata.
- Integrated parameter uncertainty registry table with exact specifications.
- Expanded section on limitations, open research questions, and active research threads.
- Added Appendix A (Notation Glossary) and Appendix B (Parameter Set Version History).

### Removed
- Retired all legacy drafts (v0.1 to v0.5).
- Removed duplicate and contradictory introductions.
- Cleaned up inconsistent naming conventions ($k_{\text{cat}}$ vs $k_{\text{CA}}$).

---

## [0.5.0] - 2025-01-25
### Added
- Defined the 5 canonical validation cases for empirical validation.
- Introduced the reproducibility protocol (deterministic seeds, SHA-256 hashes).
- Added property-based testing requirements.
- Configured 50,000 samples for high-precision research runs.

---

## [0.4.0] - 2024-12-18
### Added
- Coupled kinetic results with the downstream economic model.
- Propagated capture uncertainty directly into NPV distribution projections.
- Accounted for CCTS credit pricing volatility and block market price fluctuations.

---

## [0.3.0] - 2024-11-30
### Added
- Implemented Sobol sensitivity analysis using the Saltelli sampling scheme.
- Defined first-order and total-order indices.
- Established the Critical Experiments framework.
- Applied ±30% lognormal uncertainty to $K_{M,\text{CO}_2}$ and ±$2^\circ\text{C}$ to reactor temperature.

---

## [0.2.0] - 2024-10-22
### Added
- Replaced vanilla Monte Carlo sampling with Latin Hypercube Sampling (LHS).
- Raised sample scale baseline to 10,000.
- Defined coverage probability equations.
- Corrected potential scale reduction factor ($\hat{R}$) calculations.

---

## [0.1.0] - 2024-09-15
### Added
- Initial stochastic model draft for CBMS.
- Modeled liquid saturation dynamics via Wiener process with drift.
- Solved First Passage Time (FPT) using Wald distribution.

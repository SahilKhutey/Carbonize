# Parameter Provenance and Validation Protocols

This document details the provenance, confidence intervals, and maintenance workflows for the parameters in the CBMS-Sim platform.

## 1. Overview of Parameter Classification

We classify simulation parameters into three tiers:
1.  **Tier 1: Measured (HIGH Confidence)**: Obtained from direct in-house bench-scale testing.
2.  **Tier 2: Literature-derived (MEDIUM-HIGH Confidence)**: Mapped from peer-reviewed scientific studies.
3.  **Tier 3: Assumed/Placeholder (LOW Confidence)**: Initial estimates awaiting direct empirical validation.

Our active objective is to transition from **10% measured** to **$\ge 60\%$ measured** by the end of Phase 1.

---

## 2. Placeholder Parameter Roadmap

The following placeholders require immediate measurement:

### A. Carbonic Anhydrase Kinetics (`kinetics.k_cat`, `kinetics.K_M_co2`)
*   **Why Critical**: Core to all $\text{CO}_2$ capture velocity and hydration predictions.
*   **Measurement Plan**: CE-1 CA activity assay at $40^\circ\text{C}$ and $\text{pH } 8.5$. Lineweaver-Burk plots to define saturation.

### B. Heavy Metal Sorption (`kinetics.k_chel_Hg`, `kinetics.k_chel_Pb`, etc.)
*   **Why Critical**: Validates heavy metal capture efficiency claims for flue gas streams.
*   **Measurement Plan**: CE-2 Batch sorption isotherms using ICP-MS validation.

### C. Nucleation & Precipitation (`kinetics.k_precip_caco3`)
*   **Why Critical**: Controls mineral solid block formation kinetics.
*   **Measurement Plan**: CE-3 Continuous precipitation monitoring using turbidimetry.

---

## 3. Maintenance Workflows

### Version Control & Updates
1.  **Modify Values**: Any change to parameter values must update `inventory.csv` AND `v2026.1.json`.
2.  **Date Log**: Update `last_validated` and `next_review` columns.
3.  **CI Validation**: Run `python -m pytest` to verify the codebase remains stable after values adjust.
4.  **Increment Version**: Increment the parameter set version tags (e.g. `v2026.1` $\to$ `v2026.2`).

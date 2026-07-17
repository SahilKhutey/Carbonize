# 🌊 CBMS-Sim: Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator

CBMS-Sim is an industrial emissions control simulation platform designed to model, analyze, and validate a novel **coral-inspired biomineralization** technology for capturing multiple pollutants in a single integrated process.

**Copyright (c) 2026 Sahil Khutey. All Rights Reserved.**
Licensed under the Business Source License 1.1 (BSL 1.1). See the [LICENSE](LICENSE) file for terms.

---

## 💼 For Investors: The Business & Economic Case

The Coral-Inspired Biomineralization Multi-Pollutant Solidification System (CBMS) represents a paradigm shift in industrial emissions control for hard-to-abate sectors.

*   **Low-CAPEX Turnkey Retrofit**: CBMS requires ~40% of the CAPEX of conventional amine-scrubbing, electrocatalytic, or Metal-Organic Framework (MOF) based carbon capture systems.
*   **Dual Revenue Model**:
    1.  **CCTS Credits**: Earn compliance or voluntary carbon credits under the Indian Carbon Market (CCTS) at a baseline price of ₹1,850/tCO₂.
    2.  **Circular Solid Products**: Compaction of captured carbonate sludge into construction-grade gypsum and biomineralized bricks, eliminating geological storage costs and creating a local revenue stream.
*   **Indigenous Supply Chain**: Uses biowaste chitosan sourced from Indian seafood processors, protecting the supply chain from geopolitical volatility.

---

## 🛠️ For Engineers: The Tech Stack & Architecture

CBMS-Sim is structured as a monorepo consisting of high-performance scientific solvers, web services, and an interactive digital twin visualization dashboard.

```
                          ┌──────────────────────────┐
                          │   Client Layer (React)   │
                          │   - Digital Twin DCS     │
                          │   - Results Dashboards   │
                          └────────────┬─────────────┘
                                       │ WebSocket / REST
                          ┌────────────▼─────────────┐
                          │    API Layer (FastAPI)   │
                          │    - Tenant auth, CORS   │
                          └──────┬─────────────┬─────┘
                                 │             │
                    ┌────────────▼─────┐ ┌─────▼──────────────┐
                    │ Workers (Celery) │ │ sim-core (Numba)   │
                    │ - Report, PDF    │ │ - Stiff ODE Solver │
                    └──────────────────┘ └────────────────────┘
```

### Monorepo Structure
*   `packages/sim-core`: Numba-accelerated scientific kernels for chemical kinetics, mass balance, Wiener process simulations, and Latin Hypercube sampling.
*   `packages/api`: FastAPI application implementing user authentication, role-based access control, CRUD endpoints, and WebSockets.
*   `packages/workers`: Celery tasks for heavy report generation and background simulations.
*   `packages/web`: React 19, TypeScript, Tailwind CSS, and Vite frontend for user configuration.

### Local Setup
Ensure you have Python 3.12, Node.js 20, pnpm, and Poetry installed.

1.  **Python dependencies**:
    ```bash
    poetry install
    ```
2.  **Node.js dependencies**:
    ```bash
    pnpm install --ignore-scripts
    ```
3.  **Run Tests**:
    ```bash
    poetry run pytest
    ```
4.  **Build Frontend**:
    ```bash
    pnpm build:web
    ```

---

## 🔬 For Scientists: Biomineralization & Kinetics

The scientific core of CBMS-Sim models the accelerated capture of $\text{CO}_2$, $\text{SO}_2$, $\text{NO}_x$, heavy metals, and particulate matter (PM) in a single liquid-slurry phase.

### Key Scientific Formulations
*   **Stiff Kinetic Solver**: Models a 9-species ordinary differential equation (ODE) system capturing chemical equilibria in viscous media.
*   **Biocatalytic Kinetics**: Employs Michaelis-Menten kinetics modeling carbonic anhydrase (CA) enzyme deactivation over time using Arrhenius equations.
*   **Chitosan-Templated Mineralization**: Simulates the nucleation and crystal growth of $\text{CaCO}_3$ on chitosan polymer scaffolds.
*   **Uncertainty Quantification**: Runs parallel Monte Carlo simulations and Latin Hypercube Sampling (LHS) paired with Sobol global sensitivity analysis to map key parameters.

### Empirical Validation & Parameter Confidence
The mathematical models and calibration pipelines are structured for multi-stage empirical validation:
1.  **Literature-Derived Benchmarks**: Initial model equations and core physical constants are derived from and aligned with peer-reviewed literature (e.g., $\text{CO}_2$ hydration rates within 5% of *Mirjafari et al. 2007*, gypsum equilibrium comparisons to PHREEQC within 2%).
2.  **Parameter Confidence Tiers**: As documented in [provenance.md](data/parameters/provenance.md), currently approximately 10% of simulation parameters are directly measured in-house, with the remaining 90% literature-derived or initial design placeholders.
3.  **Validation Pipeline**: The calibration pipeline is currently validated using synthetic assays (e.g., mock CE-1 rates). Phase 1 research targets transitioning the codebase to $\ge 60\%$ in-house measured parameters as experimental data from physical CE-1, CE-2, and CE-3 trials becomes available.

### Theoretical Literature
The mathematical framework, stochastic modeling methods, and parameter registries are detailed in the peer-reviewed canonical manuscript:
*   [Stochastic Modeling in the CBMS-Sim Platform (v1.0)](manuscript/theory/stochastic_modeling_v1.0.md)

---

## 📜 License & IP

CBMS-Sim is released under the **Business Source License 1.1 (BSL 1.1)**.
See [LICENSE](LICENSE) for the full text.

### What This Means for You

| If you want to... | You need... |
|-------------------|-------------|
| 👀 Read the code | ✅ Nothing — it's source-available |
| 🔬 Run it for academic research | ✅ Nothing — non-production use is free |
| 🧪 Run a pilot (<100 hrs/month or <10 t CO₂/month) | ✅ Nothing — within Additional Use Grant |
| 🛠️ Contribute code | ✅ Sign the CLA (see [CONTRIBUTING.md](.github/CONTRIBUTING.md)) |
| 📚 Cite it in a paper | ✅ Use the [CITATION.cff](CITATION.cff) format |
| 🏭 Run it in production (>100 hrs/month) | 💰 Commercial license — email licensing@cbms.in |
| 💼 Fork for competing product | 💰 Commercial license required |
| 🔒 Share our trade secrets | ❌ Don't. They're protected. |

### Open Source Components (Tier 1)

✅ **Freely shareable under BSL 1.1:**
- All source code in this repository
- Documentation (`docs/`, `manuscript/`)
- Validation cases against published data
- API specifications
- Scientific methodology (published parts)

### Controlled Components (Tier 2)

⚠️ **Share only with permission and NDA:**
- Customer-specific simulation results
- Pilot operational data from named partners
- Detailed cost models with vendor-specific pricing
- Investor due diligence materials (under NDA)

### Trade Secrets (Tier 3)

❌ **Never share — protected as trade secrets:**
- Proprietary reaction kinetics coefficients (beyond published literature)
- Cost-optimized reagent formulations with specific suppliers
- Pilot plant tuning parameters
- Unpublished bench-scale experimental data
- Internal financial projections and cap table
- Customer pipeline and sales data

**If you're unsure whether something is shareable, ask first:**
- 📧 General IP: ip@cbms.in
- 📧 Commercial licensing: licensing@cbms.in
- 📧 Security disclosures: security@cbms.in

### Contributor License Agreement (CLA)

By submitting a pull request, you agree that:
- You retain copyright to your contributions
- You grant CBMS Technologies a non-exclusive license to use your contributions
- Your contributions are licensed under BSL 1.1 (the same as the project)

We use [CLA Assistant](https://cla-assistant.io/) to automate this. The CLA bot will comment on your first PR with a link to sign.

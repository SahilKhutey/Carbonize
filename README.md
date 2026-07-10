# 🌊 CBMS-Sim: Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator

CBMS-Sim is an industrial emissions control simulation platform designed to model and validate a novel **coral-inspired biomineralization** technology for capturing multiple pollutants in a single integrated process.

---

## ⚖️ Commercial License & Ownership

**Copyright (c) 2026 Sahil Khutey. All Rights Reserved.**

This software, its design, scientific equations, and documentation are the sole and exclusive intellectual property of **Sahil Khutey**. Unauthorized copying, modification, distribution, or reverse engineering of this software is strictly prohibited under the terms of the accompanying [LICENSE](LICENSE).

---

## 🚀 Key Features

- 🌊 **Multi-Pollutant Capture** — Simulates capture of $\text{CO}_2$, $\text{SO}_2$, $\text{NO}_x$, heavy metals, and PM in a single slurry matrix.
- 🔬 **Biocatalytic Kinetics** — Utilizes thermostable Carbonic Anhydrase (CA) and chitosan matrices to model rapid biomineralization.
- 🧱 **Solidification & Compaction** — Predicts compressive block strength grade outputs based on process inputs.
- 💰 **Economic Viability** — Calculates CAPEX, OPEX, CCTS credits (BEE compliance), block sales revenue, NPV (10-yr), and simple payback periods.
- 🎲 **Uncertainty Quantification (UQ)** — Latin Hypercube Sampling (LHS), Sobol global sensitivity analysis, and First Passage Time stochastic models.

---

## ⚙️ Architecture Overview

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

---

## 💻 Quick Start

### 1. Installation
Ensure you have Python 3.12, Node.js 20, and Poetry installed.

```bash
# Install Python dependencies
poetry install

# Install Frontend dependencies
cd packages/web
npm install --legacy-peer-deps
```

### 2. Run Test Verification
```bash
python -m pytest
```

### 3. Build Web Client
```bash
cd packages/web
npm run build
```

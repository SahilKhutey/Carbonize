# Project File Structure & Scientific Theory Layout

This document details the layout of architectural plans, code packages, and scientific theory documentation in the CBMS-Sim repository.

## 📁 Repository Map

```
Carbonize/
├── .github/                  # CI/CD workflows and issue/PR templates
├── docs/                     # Project documentation
│   ├── adr/                  # Architectural Decision Records
│   ├── architecture/         # System design specifications
│   │   └── file-structure.md # (This file) Project structure reference
│   └── pitch/                # Pitch decks and manual portals
├── manuscript/               # Scientific publications and theoretical frameworks
│   └── theory/               # Theory canonical documents
│       ├── CHANGELOG.md      # Changelog for scientific documents
│       └── stochastic_modeling_v1.0.md # CANONICAL Stochastic Modeling document
├── packages/                 # Monorepo packages
│   ├── api/                  # FastAPI Web Backend
│   ├── cfd/                  # CFD simulation settings & scripts
│   ├── dashboards/           # Telemetry dashboard configuration
│   ├── infra/                # Terraform deployment scripts
│   ├── shared/               # Shared utilities
│   ├── sim-core/             # Numerical core solver (Numba kernels)
│   ├── web/                  # React 19 Frontend Dashboard
│   └── workers/              # Celery task processing workers
```

## 🔬 Scientific Theory Locations
To prevent version fragmentation and ambiguous drafts, all scientific theories, ODE kinetic equations, and mathematical models must be documented in a single canonical format within the `manuscript/theory/` directory.

The current active canonical files are:
1.  **Stochastic Modeling Framework**: [stochastic_modeling_v1.0.md](../../manuscript/theory/stochastic_modeling_v1.0.md) (Supersedes all legacy Google Gemini PDFs).
2.  **Reaction Kinetics (planned)**: `kinetics_v1.0.md`.
3.  **Economic Model (planned)**: `economic_model_v1.0.md`.

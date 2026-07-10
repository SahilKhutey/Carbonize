# 🛠️ Technology Stack Definition: Coral-Inspired Biomineralization Multi-Pollutant Solidification System (CBMS)

This document specifies the complete, production-grade technology stack for the **Coral-Inspired Biomineralization Multi-Pollutant Solidification System (CBMS)**. It spans scientific simulation, laboratory data systems, plant control, business operations, and pilot deployment infrastructure.

---

## 1. Stack Architecture Overview

### 1.1 The 14-Layer Stack Model
```
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 14: PILOT DEPLOYMENT INFRASTRUCTURE                          │
│  (Field enclosures, piping, instrumentation, civil works)           │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 13: IP & LEGAL TECH                                           │
│  (Patent management, FTO databases, contract automation)             │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 12: PROJECT MANAGEMENT & OPERATIONS                           │
│  (PM tools, Gantt, time tracking, OKR frameworks)                   │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 11: DOCUMENTATION & COLLABORATION                            │
│  (Wiki, diagrams, code repos, version control)                      │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 10: HARDWARE, IoT & FIELD SENSORS                            │
│  (Microcontrollers, edge gateways, CEMS, lab instruments)            │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 9: AI/ML & OPTIMIZATION                                       │
│  (Bayesian optimization, surrogate models, digital twin)             │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 8: SECURITY, COMPLIANCE & IDENTITY                           │
│  (Auth, encryption, audit logs, regulatory tracking)                 │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 7: ENTERPRISE SYSTEMS (ERP/CRM/Finance)                      │
│  (Customer mgmt, accounting, HR, supply chain)                       │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 6: B2B SaaS PLATFORM (Industrial Simulator)                  │
│  (Web app, API, frontend, customer dashboards)                      │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 5: DATA ENGINEERING & ANALYTICS                              │
│  (ETL/ELT, time-series DB, data lake, BI dashboards)                │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 4: CLOUD INFRASTRUCTURE & DEVOPS                             │
│  (Compute, storage, K8s, CI/CD, IaC, monitoring)                    │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 3: PLANT CONTROL & INDUSTRIAL AUTOMATION                     │
│  (SCADA, PLCs, historians, alarm management)                         │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 2: LABORATORY INFORMATION MANAGEMENT (LIMS)                  │
│  (Sample tracking, experiment records, ELN, data capture)            │
├──────────────────────────────────────────────────────────────────────┤
│  LAYER 1: SCIENTIFIC SIMULATION & MODELING                          │
│  (Reaction kinetics, CFD, FEA, multi-physics solvers)                 │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Stack Selection Principles
*   **Open-Source First:** Prioritize open-source tools for core packages to control costs and prevent vendor lock-in.
*   **Production-Proven:** Every tool must be widely adopted and battle-tested at scale.
*   **Indian-Context Appropriate:** Ensure local data residency (e.g., AWS Mumbai region), GST compliance, and domestic payment options.
*   **Regulatory-Compliant:** Maintain immutable logging to support CPCB emissions tracking and BEE Carbon Credit Trading Scheme audits.

---

## 2. Layer 1: Scientific Simulation & Modeling

### 2.1 Core Stack
*   **Numerical Core:** Python 3.12.x (PSF License) — Primary scripting and coordination language.
*   **Array & Math:** NumPy 1.26.x (BSD License) — High-performance multidimensional arrays.
*   **Scientific Computing:** SciPy 1.14.x (BSD License) — Integrators, solvers, and statistics.
*   **JIT Compilation:** Numba 0.61.x (BSD License) — Translates python math functions to LLVM-optimized machine code.
*   **Units & Constants:** Pint 0.24.x (BSD License) — Guarantees unit safety and converts volumetric coordinates.
*   **Chemical Speciation:** PHREEQC 3.7.x (USGS Public Domain) — Geochemical speciation solver, critical for alkaline slag leach calculations.
*   **Process Flowsheet:** DWSIM 8.0.x (GPL License) — Flowsheet validation of overall chemical balance.

### 2.2 CFD Stack (Stage 3 Tower)
*   **CFD Solver:** OpenFOAM 12.x (GPL License) — Multiphase flow solver for bubble columns.
*   **Meshing Tool:** snappyHexMesh (Bundled with OpenFOAM) — Automatic grid construction.
*   **Post-Processing:** ParaView 5.12.x (BSD License) — Streamline visualization and velocity vectors.
*   **Mechanical CAD:** SolidWorks 2024 SP3 (Commercial License) — Mechanical design drawings for pilot skids.

---

## 3. Layer 2: Laboratory Information Management (LIMS)

*   **LIMS Platform:** OpenBIS 20.10.x (BSD License) — Tracks chemical inventories, samples, and cell cultures.
*   **Electronic Lab Notebook (ELN):** eLabFTW 5.0.x (AGPL License) — Version-controlled experiment logs and procedures.
*   **Instrument Interface:** PyMeasure 0.13.x (MIT License) — Automation scripting to extract data from balances, pH probes, and spectrophotometers.

---

## 4. Layer 3: Plant Control & Industrial Automation

*   **SCADA Engine:** Ignition by Inductive Automation 8.1.x (Commercial License) — High-fidelity HMI, alarming, and tag databases.
*   **Process PLCs:** Siemens S7-1200 / S7-1500 (Commercial License) — Manages pump rates, valve manifolds, and fan speeds.
*   **Safety Interlocks:** Siemens S7-1500F (Commercial License) — SIL-2 compliant emergency shutdown loop.
*   **Communication Bus:** EtherCAT / Modbus TCP — Low-latency real-time fieldbus.
*   **OPC Server:** open62541 (Mozilla License) — Lightweight OPC UA bridge.

---

## 5. Layer 4: Cloud Infrastructure & DevOps

*   **Cloud Host:** AWS Mumbai (ap-south-1) — Local hosting to satisfy Indian data sovereignty.
*   **Container Runtime:** Kubernetes (EKS 1.30) — Hosts SaaS microservices.
*   **Relational Storage:** AWS RDS PostgreSQL 17.x (with `pgvector` and Timescale extensions).
*   **Asset Storage:** AWS S3 (with Object Lock for audit logs).
*   **DevOps Pipelines:** GitHub Actions + Terraform 1.9.x for Infrastructure as Code (IaC).

---

## 6. Layer 5: Data Engineering & Analytics

*   **Data Lakehouse:** Apache Iceberg formats stored on AWS S3.
*   **OLAP Analytics:** ClickHouse 24.8.x — Sub-second queries across billions of rows of historical simulation runs.
*   **Time-Series DB:** TimescaleDB 2.17.x (on PostgreSQL) — Ingestion database for sensor and SCADA logs.
*   **BI Visualization:** Apache Superset 4.0.x — Internal analytics and dashboards.

---

## 7. Layer 6: B2B SaaS Platform (Industrial Simulator)

### 7.1 Frontend Client
*   **Framework:** React 19.x (TypeScript 5.6.x, Vite build engine).
*   **State Management:** TanStack Query 5 (Server cache) + Zustand 5 (Client state).
*   **Styling & UI:** Tailwind CSS 4.0.x + shadcn/ui.
*   **Visual Charts:** Recharts 2.13.x + Apache ECharts 5.5.x.

### 7.2 Backend REST API
*   **Framework:** FastAPI 0.115.x (Python-based ASGI).
*   **Background Jobs:** Celery 5.4.x + Redis cache broker.
*   **Migration Engine:** Alembic 1.13.x.

---

## 8. Layer 7: Enterprise Systems (ERP/CRM/Finance)

*   **ERP Platform:** Odoo Community 18.0 / ERPNext 15.x — Supply chain, POs, and equipment inventory.
*   **Financial Accounting:** Zoho Books — Handles Indian GST invoicing, TDS, and bank feeds.
*   **Payroll & HR:** Keka — Domestic salary calculations, PF/ESI tracking.
*   **SaaS Billing:** Chargebee — Handles credit subscriptions.

---

## 9. Layer 8: Security, Compliance & Identity

*   **Single Sign-On (SSO):** Keycloak 26.x (Open Source Identity Brokering).
*   **MFA Protocol:** TOTP + WebAuthn.
*   **Secrets Manager:** HashiCorp Vault 1.17.x / AWS Secrets Manager.
*   **Application WAF:** AWS WAF + AWS Shield Standard (DDoS protection).
*   **Security Auditing:** Trivy (image checks) + WAF GuardDuty logs.

---

## 10. Layer 9: AI/ML & Optimization

*   **Deep Learning:** PyTorch 2.4.x — Neural network architectures.
*   **Bayesian Optimization:** BoTorch 0.12.x / Optuna 4.0.x — Formulates experiment designs for laboratory parameter testing.
*   **Surrogate Modeling:** SMT (Surrogate Modeling Toolbox) — Kriging surrogates to speed up physical ODE loops.

---

## 11. Layer 10: Hardware, IoT & Field Sensors

*   **Edge Gateway:** Advantech UNO-260 / Raspberry Pi 5.
*   **Flue Gas Sensors:** Sensirion SCD41 ($\text{CO}_2$ NDIR), Membrapor SO2/A-5 ($\text{SO}_2$ electrochemical).
*   **Process Sensors:** Endress+Hauser Memosens (pH, conductivity), PT100 Class A (Temperature RTDs).
*   **Telemetry Protocols:** MQTT Sparkplug B / OPC UA over cellular 4G/5G.

---

## 12. Layer 11: Documentation & Collaboration

*   **Wiki Platform:** BookStack 24.05 (Structured Markdown manuals).
*   **Technical Diagrams:** draw.io / Mermaid.
*   **Shared Workspace:** Google Workspace (professional Gmail, Drive).
*   **Chat Workspace:** Slack.

---

## 13. Layer 12: Project Management & Operations

*   **Agile Tracker:** Plane (Open-source alternative to Jira).
*   **Project Timelines:** OpenProject 14.x (Agile Gantt tracking).
*   **Work Logging:** Clockify.

---

## 14. Layer 13: IP & Legal Tech

*   **Patent Analytics:** Lens.org / Google Patents.
*   **Contracts & NDAs:** Leegality (India-compliant Aadhaar e-signatures).
*   **Docket Management:** CPA WIPO ePCT.

---

## 15. Layer 14: Pilot Deployment Infrastructure

### 15.1 Mechanical Skid Materials
*   **Piping Systems:** Schedule 40 Carbon Steel (structural) + PVDF/FRP (acid/slurry lines).
*   **Pumps:** Grundfos CR (reagents), Warman (fly ash abrasive slurry).
*   **Valves:** Pentair / Asahi chemical valves.
*   **Compression Press:** Custom double-acting H-frame hydraulic press (50-ton rating).

### 15.2 Civil & Electrical Infrastructure
*   **LV Switchgear:** Siemens / L&T distribution boards.
*   **Cable Routing:** Galvanized Iron (GI) ladder-type trays.
*   **Grounding:** Copper plate earthing systems.
*   **Backup Power:** Online double-conversion UPS (10 kVA, 60-min battery backup).

# 🚀 CBMS-Sim — Development Roadmap

From Concept Repo → Working, Validated, Deployable System

Prepared by: Systems Design / Hard-Tech / Research Working Group
Document Version: 1.0
Date: Q1 2026
Status of repo at time of analysis: Pre-alpha scaffold, 3 commits, no empirical validation layer confirmed, no CI confirmed.
Goal of this document: A dependency-ordered, role-tagged task list to move from "architecture sketch + PDFs" to "a system a real engineering team and real investors can trust."

---

## 📖 HOW TO READ THIS DOCUMENT

### Task Organization
1.  **Phases**: Tasks are grouped into Phases (0–8).
2.  **Prerequisites**: Phases 0–2 are prerequisites for everything else — do NOT parallelize past them until closed.
3.  **Ownership**: Each task has an owner role (matching your defined role stack).
4.  **Priority**: 🔴 Blocker · 🟠 High · 🟡 Medium · 🟢 Later.
5.  **DoD**: "Definition of Done" (DoD) is given for non-obvious items.

### Role Legend
*   **SD**: Systems Designer
*   **PTL**: Project Team Lead
*   **ML**: Machine Learning Expert
*   **PY**: Python/C/C++/Java Expert
*   **UX**: UI/UX Designer
*   **AR**: AR/XR Specialist
*   **AE**: Aerospace Engineer
*   **EG**: Engineer (General)
*   **SD-SIM**: Simulation Designer
*   **PHY**: Physicist
*   **CHEM**: Chemist
*   **MATH**: Mathematician
*   **R**: Researcher

---

## ✅ PHASE 0 — REPO & PROJECT HYGIENE (1–2 weeks)

Why this phase exists: Costs almost nothing and prevents the project from rotting before it starts.

| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **0.1** | Restructure repo: move all root-level .html files into apps/web/public/ or docs/pitch/; remove duplicates | SD | 🔴 | No standalone HTML at repo root |
| **0.2** | Establish monorepo structure (Poetry workspaces + pnpm workspaces) | SD | 🔴 | pyproject.toml and pnpm-workspace.yaml present; poetry install succeeds |
| **0.3** | Create root README that distinguishes 3 audiences: investors, engineers, scientists | PTL | 🔴 | Single README with three clearly labeled sections |
| **0.4** | Add CODEOWNERS, CONTRIBUTING, LICENSE (BSL 1.1), SECURITY.md | PTL | 🔴 | All 4 files present at repo root |
| **0.5** | Set up .gitignore, .gitattributes, .editorconfig | SD | 🟠 | Pre-commit hooks pass on a clean clone |
| **0.6** | Define branch strategy: main (protected), develop, feature/*, release/*, hotfix/* | PTL | 🟠 | Documented in CONTRIBUTING.md; branch protection rules on main |
| **0.7** | Initialize GitHub repo with: description, topics, website, license | PTL | 🟠 | Repo metadata complete |
| **0.8** | Add issue templates: Bug Report, Feature Request, Research/Science, Security | PTL | 🟠 | All 4 templates configured |
| **0.9** | Add PR template with Definition of Done checklist | PTL | 🟠 | Template renders correctly on new PR |
| **0.10** | Set up GitHub Discussions with categories: General, Ideas, Q&A, Research | PTL | 🟢 | Categories configured and pinned |
| **0.11** | Enable Dependabot for both Python and npm | SD | 🟠 | First dependency PR generated |
| **0.12** | Create docs/adr/ directory with ADR template | SD | 🟠 | Template + 1 example ADR committed |
| **0.13** | Add docs/roadmap.md (this document) | PTL | 🟠 | Committed to repo |
| **0.14** | Create .github/CODEOWNERS assigning packages to teams | PTL | 🟠 | CODEOWNERS file active |

---

## ✅ PHASE 1 — CI/CD & QUALITY GATES (2–3 weeks)

Why this phase exists: Nothing else matters if the build is broken and nobody knows.

| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Set up GitHub Actions: lint, type-check, test, build for every PR | SD | 🔴 | All 4 jobs run on every PR; status checks block merge |
| **1.2** | Pre-commit hooks: ruff, black, isort, mypy, eslint, prettier | SD | 🔴 | pre-commit run --all-files passes on clean checkout |
| **1.3** | Enable CodeQL security scanning (weekly + on PR) | SD | 🟠 | CodeQL workflow runs; alerts visible in Security tab |
| **1.4** | Enable secret scanning (GitHub native + gitleaks pre-commit) | SD | 🔴 | No secrets in commit history; alerts configured |
| **1.5** | Set up Codecov with coverage gates (80% minimum) | SD | 🟠 | Coverage badge in README; CI fails if <80% |
| **1.6** | Add Dependabot auto-merge for patch updates | SD | 🟢 | Minor/patch updates auto-merged; majors require review |
| **1.7** | Create devcontainer for Codespaces (Python 3.12, Node 20, Poetry, Docker) | SD | 🟠 | Codespace boots in <3 min; make test works |
| **1.8** | Configure branch protection on main: 2 reviews, CI required, no force-push | PTL | 🔴 | Settings verified in GitHub |
| **1.9** | Add Makefile with: install, test, lint, format, run, sim | SD | 🟠 | All targets work in Codespace |
| **1.10** | Add docker-compose.dev.yml for local Postgres + Redis | SD | 🟠 | docker compose up starts full stack |
| **1.11** | Set up release drafter for auto-generated release notes | SD | 🟢 | PRs auto-categorize in next release draft |
| **1.12** | Add CODEOWNERS auto-assignment to PRs | PTL | 🟢 | PRs auto-assign to package owners |

---

## ✅ PHASE 2 — EMPIRICAL VALIDATION LAYER (3–4 weeks) — CRITICAL PATH

Why this phase exists: This is the single biggest credibility gap. A simulator with no validation against real data is a toy, not a tool. No external pitch is ethical without this.

| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **2.1** | Collect 10–20 published datasets of CO₂ absorption, gypsum precipitation, chitosan-metal binding | R + CHEM | 🔴 | BibTeX file with DOIs in data/citations/; each citation has a 1-line "what we use it for" note |
| **2.2** | Define 5 canonical "validation cases" (one per major claim) | R | 🔴 | docs/validation/cases.md with inputs, expected outputs, tolerances, sources |
| **2.3** | Build sim-core/validation/ module with reproducible case runners | PY | 🔴 | Each case: runs simulation, compares to reference, reports pass/fail within tolerance |
| **2.4** | Case 1: CO₂ hydration kinetics vs. Mirjafari 2007 Figure 3 | R + PY | 🔴 | ≤5% deviation from published curve |
| **2.5** | Case 2: CaCO₃ precipitation vs. Zeng 2024 SEM observations | R + CHEM | 🔴 | Crystal morphology consistent within model assumptions |
| **2.6** | Case 3: Gypsum equilibrium vs. PHREEQC at matched conditions | MATH | 🔴 | Equilibrium concentrations within 2% |
| **2.7** | Case 4: SO₂ scrubbing efficiency vs. EPA Air Pollution Control manual | AE | 🔴 | L/G ratio → efficiency curve matches within 8% |
| **2.8** | Case 5: Heavy metal sorption on chitosan vs. published batch isotherms | CHEM | 🔴 | Freundlich/Langmuir fit within 10% |
| **2.9** | Generate "Validation Report" PDF showing case-by-case results | SD | 🟠 | Auto-generated on make validate; included in releases |
| **2.10** | Add make validate to CI (runs all 5 cases; fails build if regression) | SD | 🟠 | CI badge shows validation status |
| **2.11** | Document parameter provenance for every constant in the model | R | 🟠 | data/parameters/v2026.1.json includes source_doi for each value |
| **2.12** | Create sensitivity baseline report (which parameters most affect output) | MATH | 🟠 | Report identifies top 5 most-influential parameters |

---

## ✅ PHASE 3 — SIM-CORE IMPLEMENTATION (4–6 weeks)

Why this phase exists: This is the scientific heart. Every downstream layer depends on it being correct and fast.

### 3A. Scientific Kernels
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **3.1** | Implement reaction_rhs_numba — 9-species ODE right-hand side | PY + MATH | 🔴 | Compiles; matches validation Case 1 |
| **3.2** | Implement Henry's law for CO₂, SO₂, NOₓ as function of T | CHEM | 🟠 | Validated against Case 4 |
| **3.3** | Implement Michaelis-Menten + product inhibition for CA kinetics | R | 🟠 | Matches Mirjafari 2007 |
| **3.4** | Implement Arrhenius enzyme deactivation | R | 🟠 | Matches Rigkos 2024 thermostable variant |
| **3.5** | Implement CaCO₃ nucleation + growth with chitosan template effect | R + CHEM | 🟠 | Validated against Case 2 |
| **3.6** | Implement SO₂ → CaSO₄·2H₂O co-precipitation | CHEM | 🟠 | Validated against Case 6 |
| **3.7** | Implement heavy metal chelation (Hg, Pb, Cd, As) on chitosan | CHEM | 🟠 | Validated against Case 5 |
| **3.8** | Implement PM (fly ash) viscous capture | AE | 🟡 | Physically reasonable retention curve |
| **3.9** | Wrap Numba kernels with @njit(cache=True) and warmup script | PY | 🔴 | Warm cache in CI; first run < 2s, subsequent < 200ms |

### 3B. Solver & Mass Balance
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **3.10** | Wrap scipy.integrate.solve_ivp (BDF) for stiff systems | PY | 🔴 | Converges on all validation cases |
| **3.11** | Implement mass balance engine with stoichiometric closure | PY + CHEM | 🔴 | Conservation error < 0.5% on all cases |
| **3.12** | Add convergence diagnostics (R̂, ESS, wall-clock) | MATH | 🟠 | Returned in every KineticsResult |
| **3.13** | Build solve_kinetics() convenience function with warmup | PY | 🟠 | One-line call returns KineticsResult |

### 3C. Uncertainty Quantification
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **3.14** | Implement LHS sampling via scipy.stats.qmc | MATH | 🟠 | Verified against published LHS examples |
| **3.15** | Implement parallel Monte Carlo with ProcessPoolExecutor | PY | 🟠 | Linear speedup on 16 cores |
| **3.16** | Implement Sobol sensitivity (Saltelli sampling, first/total order) | MATH | 🟠 | Matches SALib reference outputs |
| **3.17** | Implement FPT analysis (Inverse Gaussian) for saturation | MATH | 🟡 | Validated against Wiener process toy model |
| **3.18** | Critical experiments recommender (top-k most-influential params) | ML | 🟠 | Matches Sobol ranking |

### 3D. Block Properties
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **3.19** | Implement block strength model (pozzolanic + polymer) | EG | 🟠 | Predicts M20/M25 grades from inputs |
| **3.20** | Implement IS grade classifier (1077, 2185, M-class) | EG | 🟠 | Classification matches manual |
| **3.21** | Implement leach risk predictor (qualitative: low/med/high) | CHEM | 🟠 | Conservative defaults |

### 3E. Economic Engine
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **3.22** | Implement CAPEX model (0.6 power-law scaling) | EG | 🟠 | Within ±15% of vendor quotes |
| **3.23** | Implement OPEX model (reagents + utilities + labor) | EG | 🟠 | Bottom-up per line item |
| **3.24** | Implement NPV/IRR/payback | EG | 🟠 | Matches Excel reference for 3 test cases |
| **3.25** | Integrate CCTS credit pricing (₹1,850/tCO₂ baseline) | EG | 🟠 | Configurable; latest BEE price |

### 3F. Pipeline Orchestrator
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **3.26** | Build SimulationOrchestrator coordinating all stages | PY | 🔴 | End-to-end run produces SimulationResult |
| **3.27** | Add progress callbacks (stage, percentage) | PY | 🟠 | Used by API for WebSocket updates |
| **3.28** | Implement checkpointing for resume after failure | PY | 🟡 | Can resume from stage 3 after stage 2 crash |
| **3.29** | Add reproducibility verification (bit-exact with same seed) | PY | 🔴 | Property test passes 1000 times |

---

## ✅ PHASE 4 — API & WORKER LAYER (3–4 weeks)

### 4A. FastAPI Backend
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **4.1** | Set up FastAPI app skeleton with lifespan, CORS, middleware | PY | 🔴 | /health returns 200; OpenAPI spec generated |
| **4.2** | Implement JWT auth (access + refresh tokens) | PY + SD | 🔴 | Login, refresh, logout endpoints work |
| **4.3** | Implement RBAC (5 roles: owner, admin, engineer, analyst, viewer) | SD + PY | 🟠 | Permission checks on all endpoints |
| **4.4** | Implement tenant isolation via RLS + org_id scoping | SD | 🔴 | Cross-tenant access returns 404, not 403 |
| **4.5** | Build /api/v1/plants CRUD with optimistic locking | PY | 🟠 | Concurrent edits → version conflict |
| **4.6** | Build /api/v1/reagents CRUD with cost calculation | PY | 🟠 | Cost computed on-demand |
| **4.7** | Build /api/v1/simulations (submit, status, results, cancel) | PY | 🔴 | Full lifecycle works end-to-end |
| **4.8** | Build /api/v1/simulations/baseline (sync, <5s) | PY | 🟠 | Returns point estimates immediately |
| **4.9** | Build /api/v1/simulations/{id}/sensitivity (async Sobol) | PY | 🟡 | Returns indices when complete |
| **4.10** | Build /api/v1/reports (generate, list, download) | PY | 🟠 | PDF generation pipeline works |
| **4.11** | Build /api/v1/compliance/ccts (summary, claim submit, audit) | PY | 🟠 | CCTS aggregation correct |
| **4.12** | Build /api/v1/twin/{id} (state, stream, override) | PY | 🟡 | Real-time updates via WebSocket |
| **4.13** | Implement rate limiting (per-user, per-endpoint) | SD | 🟠 | SlowAPI configured; 429 on exceed |
| **4.14** | Implement RFC 7807 error responses | SD | 🟠 | All errors return Problem Details |
| **4.15** | Add request ID propagation for tracing | SD | 🟠 | X-Request-ID in all responses |
| **4.16** | Configure OpenTelemetry (traces + metrics) | SD | 🟠 | Spans visible in Jaeger/Tempo |
| **4.17** | Add Prometheus /metrics endpoint | SD | 🟠 | Grafana can scrape |

### 4B. Celery Workers
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **4.18** | Set up Celery with Redis broker, 6 priority queues | PY | 🔴 | Worker connects; tasks can be dispatched |
| **4.19** | Implement run_full_simulation task (main pipeline) | PY | 🔴 | Simulation completes via worker |
| **4.20** | Implement generate_pdf task with Typst | PY | 🟠 | PDF generated, uploaded to S3 |
| **4.21** | Implement generate_ccts_claim task | PY | 🟠 | Evidence package built, submitted |
| **4.22** | Implement run_sobol_analysis task (standalone UQ) | PY | 🟡 | Returns Sobol indices |
| **4.23** | Implement progress emission via Redis pub/sub | PY | 🟠 | WebSocket receives real-time updates |
| **4.24** | Add retry policies (exponential backoff, max retries) | PY | 🟠 | Transient failures recover automatically |
| **4.25** | Add dead letter queue for poison messages | PY | 🟡 | Failed jobs visible for manual inspection |
| **4.26** | Implement run_bayesian_optimization task (BoTorch) | PY + ML | 🟢 | Finds optimal operating conditions |
| **4.27** | Implement twin_sync task (IoT → state) | PY | 🟡 | Periodic state updates from sensors |
| **4.28** | Add worker health checks (liveness, readiness) | PY | 🟠 | K8s can detect unhealthy workers |

### 4C. Database
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **4.29** | Design schema (12 tables, relationships, indexes) | SD | 🔴 | ER diagram reviewed; migrations testable |
| **4.30** | Set up Alembic migrations | PY | 🔴 | alembic upgrade head works on fresh DB |
| **4.31** | Implement SQLAlchemy 2.0 async models | PY | 🔴 | All 12 tables modeled |
| **4.32** | Enable Row-Level Security for multi-tenancy | SD | 🔴 | Cross-tenant queries return empty |
| **4.33** | Add TimescaleDB hypertables for sensor data | PY | 🟡 | Efficient time-series queries |
| **4.34** | Set up repository pattern (no raw SQL in services) | PY | 🟠 | All DB access via repositories |
| **4.35** | Add database seed script (sample plants, reagents) | PY | 🟠 | Fresh DB has demo data |
| **4.36** | Configure connection pooling (asyncpg pool) | SD | 🟠 | No connection exhaustion under load |

---

## ✅ PHASE 5 — FRONTEND (4–5 weeks)

### 5A. Project Setup
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **5.1** | Vite + React 19 + TypeScript scaffold | UX | 🔴 | pnpm dev runs; HMR works |
| **5.2** | Tailwind CSS + shadcn/ui setup | UX | 🟠 | Design system applied |
| **5.3** | TanStack Query for server state | UX | 🟠 | Caching, refetching work |
| **5.4** | Zustand for client state | UX | 🟢 | Auth/UI stores implemented |
| **5.5** | React Router v6 with lazy loading | UX | 🟠 | Code-split routes |
| **5.6** | i18n setup (en-IN, hi-IN) | UX | 🟢 | Language toggle works |
| **5.7** | ESLint + Prettier + TypeScript strict | UX | 🔴 | Lint passes; strict mode on |

### 5B. Authentication & Layout
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **5.8** | Login page with email/password, MFA support | UX | 🔴 | Successful login → dashboard |
| **5.9** | AppShell (sidebar, header, breadcrumbs) | UX | 🟠 | Navigation works; responsive |
| **5.10** | Auth store + useAuth hook | UX | 🟠 | Token refresh; logout |
| **5.11** | Protected route wrapper | UX | 🟠 | Unauthenticated → /login |

### 5C. Core Pages
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **5.12** | Dashboard (KPIs, recent sims, quick actions) | UX | 🟠 | All data sources render correctly |
| **5.13** | Plant list + create + detail | UX | 🟠 | CRUD via UI; form validation |
| **5.14** | Reagent designer (sliders, cost preview) | UX | 🟠 | Real-time cost calculation |
| **5.15** | Simulation list + new + detail | UX | 🔴 | Full submission flow works |
| **5.16** | Results dashboard (distributions, KPIs, financials) | UX | 🔴 | All charts render with real data |
| **5.17** | Sensitivity page (Sobol bar chart, critical list) | UX | 🟡 | Visually clear parameter impact |
| **5.18** | Reports list + viewer | UX | 🟠 | PDF download via presigned URL |
| **5.19** | Compliance dashboard (CCTS, audit trail) | UX | 🟠 | Submission flow works |
| **5.20** | Digital twin view (real-time sensors, controls) | UX | 🟡 | WebSocket updates render live |

### 5D. Reusable Components
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **5.21** | KPICard with uncertainty display | UX | 🔴 | Shows mean, CI, target, confidence |
| **5.22** | DistributionChart (histogram with CI bands) | UX | 🔴 | Honest uncertainty visualization |
| **5.23** | LiveProgressTracker (WebSocket-driven) | UX | 🔴 | Stage-by-stage progress; reconnect on disconnect |
| **5.24** | UncertaintyInterval (p5–p95 range display) | UX | 🟠 | Visual honesty in all metrics |
| **5.25** | ConfidenceIndicator (HIGH/MED/LOW based on CV) | UX | 🟠 | Color-coded reliability |
| **5.26** | CitationLink (DOI hyperlink with tooltip) | UX | 🟠 | Provenance always visible |
| **5.27** | NPVWaterfall chart | UX | 🟡 | Clear financial story |
| **5.28** | SensitivityBarChart (first/total order) | UX | 🟡 | Critical params obvious |
| **5.29** | RealTimeTimeSeries (auto-refresh, pause) | UX | 🟡 | Smooth 1Hz updates |
| **5.30** | ActuatorGrid (twin controls) | UX | 🟡 | Operator-friendly controls |

### 5E. Quality
| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **5.31** | Unit tests (Vitest) for all hooks and components | UX | 🟠 | >70% component coverage |
| **5.32** | E2E tests (Playwright) for critical journeys | UX | 🟠 | Signup → sim → results works |
| **5.33** | Storybook for component library | UX | 🟢 | All components documented |
| **5.34** | Accessibility audit (WCAG 2.1 AA) | UX | 🟠 | axe-core passes; keyboard nav works |
| **5.35** | Performance audit (Lighthouse >90) | UX | 🟠 | LCP < 2.5s, CLS < 0.1 |
| **5.36** | Visual regression tests (Chromatic/Percy) | UX | 🟢 | No unintended UI changes |

---

## ✅ PHASE 6 — INFRASTRUCTURE (2–3 weeks)

| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **6.1** | Terraform: VPC, subnets, NAT, security groups | SD | 🔴 | terraform apply succeeds; no public DB |
| **6.2** | Terraform: RDS PostgreSQL 17 (Multi-AZ) | SD | 🔴 | Automated backups; encryption at rest |
| **6.3** | Terraform: ElastiCache Redis cluster | SD | 🔴 | Connection from ECS works |
| **6.4** | Terraform: ECS Fargate cluster for API + workers | SD | 🟠 | Tasks can deploy and run |
| **6.5** | Terraform: ALB + WAF + ACM certificate | SD | 🟠 | HTTPS works; WAF rules active |
| **6.6** | Terraform: S3 buckets (reports, logs, backups) | SD | 🟠 | Versioning + lifecycle rules |
| **6.7** | Terraform: CloudFront for static assets | SD | 🟢 | CDN serves web bundle |
| **6.8** | Terraform: IAM roles + Secrets Manager | SD | 🔴 | No secrets in code/env |
| **6.9** | Set up Grafana Cloud or self-hosted | SD | 🟠 | Dashboards visible; alerts fire |
| **6.10** | Configure Prometheus + Alertmanager | SD | 🟠 | Critical alerts page on-call |
| **6.11** | Set up Loki or CloudWatch Logs | SD | 🟠 | Logs queryable; retention set |
| **6.12** | Set up Jaeger or Tempo for tracing | SD | 🟡 | Request traces visible |
| **6.13** | Configure CI/CD to deploy to staging on main | SD | 🔴 | Auto-deploy to staging works |
| **6.14** | Add manual approval for production deploy | SD | 🔴 | Production requires approval |
| **6.15** | Set up backup automation (daily DB, hourly S3) | SD | 🔴 | Backups verified restorable |
| **6.16** | Document DR runbook (RTO 4h, RPO 1h) | SD | 🟠 | Runbook tested quarterly |
| **6.17** | Set up cost alerts (AWS Budgets) | SD | 🟠 | Alert at 80% of monthly budget |
| **6.18** | Tag all resources for cost allocation | SD | 🟠 | Cost per tenant queryable |
| **6.19** | Enable VPC flow logs | SD | 🟡 | Network traffic visible |

---

## ✅ PHASE 7 — PILOT READINESS (3–4 weeks)

Why this phase exists: A demo on a laptop is not a pilot. We need to survive a real plant environment.

| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **7.1** | Design containerized pilot skid (20-ft ISO spec) | AE + EG | 🟠 | CAD drawings + BOM finalized |
| **7.2** | Procure long-lead components (sensors, pumps, materials) | EG | 🟠 | POs placed; delivery dates confirmed |
| **7.3** | Build edge gateway (RPi 5 + 4G modem) | EG | 🟠 | Telemetry flows to cloud in test |
| **7.4** | Wire OPC UA → cloud ingestion | PY + EG | 🟠 | Test plant data visible in dashboard |
| **7.5** | Create pilot operator quick-start guide | UX | 🟠 | Tested by non-engineer in <30 min |
| **7.6** | Create pilot runbook (startup, shutdown, emergency) | AE | 🔴 | Reviewed by plant safety officer |
| **7.7** | Define pilot KPIs and success criteria | SD + PTL | 🔴 | Agreed with pilot partner in writing |
| **7.8** | Establish data sharing agreement with pilot partner | PTL | 🔴 | Legal-reviewed contract signed |
| **7.9** | Set up pilot-specific monitoring (uptime, data quality) | SD | 🟠 | Alerts on data gaps >5 min |
| **7.10** | Build "Health Check" page for operators (system status) | UX | 🟠 | Visible within 1 click from anywhere |
| **7.11** | Create alarm escalation policy | PTL + AE | 🟠 | Who gets paged, when, how |
| **7.12** | Conduct HAZOP review for pilot operation | AE + CHEM | 🔴 | All hazards identified and mitigated |
| **7.13** | Get pilot site safety approval | EG | 🔴 | Written authorization from plant |
| **7.14** | Train pilot operator (2-day workshop) | UX + AE | 🟠 | Operator can run independently |
| **7.15** | Document pilot data collection protocol | R | 🟠 | Reproducible measurement procedure |
| **7.16** | Set up pilot data archival (raw → processed → analyzed) | SD | 🟠 | Full audit trail from sensor to report |
| **7.17** | Create pilot weekly report template | PTL | 🟢 | Auto-generated with key metrics |
| **7.18** | Plan pilot review meeting (30-day checkpoint) | PTL | 🟠 | Calendar invite sent; agenda drafted |
| **7.19** | Prepare pilot presentation deck (for partner) | PTL | 🟠 | Slides reviewed; demo rehearsed |
| **7.20** | Establish pilot feedback collection process | PTL | 🟠 | Weekly check-in scheduled |

---

## ✅ PHASE 8 — GO-TO-MARKET (Ongoing from Month 4)

| # | Task | Owner | Priority | DoD |
| :--- | :--- | :--- | :--- | :--- |
| **8.1** | Build pitch deck (investor-focused) | PTL | 🔴 | 12 slides, 10-min version + full version |
| **8.2** | Create demo video (3-minute product tour) | UX + PTL | 🟠 | Published on website and YouTube |
| **8.3** | Write 1-page executive summary | PTL | 🔴 | PDF and HTML versions |
| **8.4** | Build public website (cbms.in) | UX | 🟠 | Landing page, pricing, docs link |
| **8.5** | Create 5 customer case studies (after pilots) | PTL | 🟢 | Published on website |
| **8.6** | Publish technical white paper | R + PTL | 🟠 | 20-page PDF; submitted to 2 journals |
| **8.7** | Set up CRM (HubSpot or similar) | PTL | 🟠 | Lead capture from website |
| **8.8** | Create sales collateral (one-pagers per industry) | PTL | 🟠 | Steel, cement, power, textiles |
| **8.9** | Identify and approach 10 potential pilot partners | PTL | 🟠 | Letters sent; meetings scheduled |
| **8.10** | Apply for DST/Startup India grants | PTL | 🟠 | Applications submitted with budget |
| **8.11** | Prepare for investor meetings (data room, financials) | PTL | 🟡 | Pitchbook, model, cap table ready |
| **8.12** | Build "ROI Calculator" on website | UX + PTL | 🟢 | Public-facing value prop tool |
| **8.13** | Create comparison page (vs. amine, MOF, MCi) | PTL | 🟢 | Honest comparison; we win on integration |
| **8.14** | Establish thought leadership (blog, LinkedIn, conferences) | PTL + R | 🟢 | 2 posts/month; 1 talk/quarter |
| **8.15** | Build email nurture sequence for leads | PTL | 🟢 | 5-email sequence; 30% open rate target |
| **8.16** | Set up customer support (Intercom or similar) | PTL | 🟠 | First-response time <4 hours |
| **8.17** | Create pricing page (transparent, tiered) | PTL | 🟠 | 3 tiers; annual discount |
| **8.18** | Build "Request Demo" flow with calendar booking | PTL | 🟠 | Calendly or similar integrated |
| **8.19** | Prepare SBIR/STTR proposal (US market) | PTL | 🟢 | Drafted; submitted |
| **8.20** | Plan CCTS methodology approval with BEE | PTL + R | 🔴 | Submitted; feedback addressed |

---

## 📊 DEPENDENCY GRAPH

```
Phase 0 (Hygiene) ──────────► Phase 1 (CI/CD) ──────────► Phase 2 (Validation)
                                        │                       │
                                        ▼                       ▼
                              Phase 3 (Sim-Core) ◄────────────┘
                                        │
                                        ▼
                              Phase 4 (API/Workers) ◄── Phase 4C (DB)
                                        │
                                        ▼
                              Phase 5 (Frontend) ◄────┐
                                        │             │
                                        ▼             │
                              Phase 6 (Infra) ────────┘
                                        │
                                        ▼
                              Phase 7 (Pilot) ◄──── Phase 8 (GTM, ongoing)
```

**Critical Path**: Phase 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7

---

## 🚦 RISK REGISTER

| Risk | Probability | Impact | Mitigation | Owner |
| :--- | :--- | :--- | :--- | :--- |
| **Chitosan degrades in flue gas** | High | Critical | Modify with cross-linkers; test in Phase 7 | CHEM |
| **CA enzyme deactivation** | High | High | Source thermophilic bulk; design recovery loop | PTL + R |
| **Heavy metals leach from blocks** | Medium | Critical | Validate TCLP early (Phase 2.8) | CHEM |
| **Mesh screens clog in real conditions** | Medium | High | Ultrasonic demolding; backup design | AE |
| **CPCB rules block "co-product" status** | Medium | Critical | Pre-consultation done; legal review | PTL |
| **UrjanovaC IP blocks our path** | Medium | High | FTO analysis done; design-around ready | PTL |
| **DST/SIDBI funding delayed** | High | Medium | Multiple parallel applications | PTL |
| **Key engineer departure** | Low | High | Documentation, cross-training, competitive comp | PTL |
| **CCTS methodology not approved** | Medium | High | Early engagement; fallback to voluntary market | PTL + R |
| **Pilot partner pulls out** | Medium | High | Backup partners identified; flexible contracts | PTL |
| **Numba fails on production hardware** | Low | Critical | Fallback to pure Python; test early | PY |
| **Insufficient pilot data for validation** | Medium | Critical | Long measurement period; secondary datasets | R |

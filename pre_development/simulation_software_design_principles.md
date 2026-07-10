# 📐 Simulation Software Design Principles: CBMS-Sim Engineering Philosophy

This document defines the engineering principles, architectural patterns, and trade-off matrices that govern implementation decisions for the **Coral-Inspired Biomineralization Simulator (CBMS-Sim)**.

---

## 1. The 12 Foundational Principles

### 1.1 Scientific Computing Principles
*   **P1: Honest Outputs:** Never produce point estimates from uncertain kinetics data. Output ranges (e.g. mean, standard deviation, and percentiles) to represent uncertainty.
*   **P2: Full Traceability:** Every simulation result must carry clear data lineage, linking outputs to exact parameters, input hashes, and cited source papers.
*   **P3: Defensible Science:** Every chemical equilibrium and kinetics model constant must be backed by cited, peer-reviewed literature. No arbitrary "magic numbers."
*   **P4: Conservative Defaults:** When parameters are ambiguous, prioritize conservative values that err on the side of process safety and compliance (e.g. minimum capture rates).

### 1.2 Software Engineering Principles
*   **P5: Modular Boundaries:** Each subsystem (e.g. mass balance, economic projections, database models, and reports) must be independently developed and tested, adhering to Hexagonal Architecture constraints.
*   **P6: Test-First Engineering:** All code paths must pass unit, integration, and property tests before deployment.
*   **P7: Performance Budgets:** Computations must operate within strict execution timelines (e.g. standard simulation runs in under 45 seconds).
*   **P8: Secure by Default:** Establish Row-Level Security (RLS) and strict input validation at the API entry point to enforce multi-tenant isolation.

### 1.3 Operational Principles
*   **P9: Observable Internals:** Output structured JSON logs, tracing request flows through distinct span IDs.
*   **P10: Resilient Operation:** Implement retry-on-failure wrappers (exponential backoff) and graceful fallbacks for external network calls.
*   **P11: Bit-Exact Reproducibility:** Ensure identical simulation results across different nodes by explicitly seeding all random number generators.
*   **P12: Long-Term Maintainability:** Write clean, typed Python code with complete docstrings. Optimize for readability first.

---

## 2. Principle Priority Order

When design goals conflict, resolve them using this priority list:

```
 P1: Honest Outputs (Highest Priority)
   └── P2: Full Traceability
         └── P3: Defensible Science
               └── P8: Secure by Default
                     └── P11: Bit-Exact Reproducibility
                           └── Soft Constraints (Performance, Modularity, Cost)
```

### 2.1 Trade-off Examples
*   *Performance vs. Honesty:* Honesty wins. We calculate full Monte Carlo uncertainty ranges even if it increases processing time.
*   *Speed vs. Reproducibility:* Reproducibility wins. We avoid non-deterministic parallel sorting algorithms that could break seed-to-hash consistency.
*   *Modularity vs. Performance:* Modularity wins. We do not write cross-boundary shortcuts to bypass API layers for speed.

---

## 3. Anti-Patterns (Explicitly Avoided)

*   **God Classes:** A single manager class handling inputs, database updates, kinetics integrations, and PDF report assembly. Clean codebase split keeps these domains separated.
*   **Silent Failures:** Catching all exceptions with blank `except:` blocks that mask coding errors.
*   **Magic Numbers:** Injecting hardcoded numbers (e.g. constant `k_cat = 1e6` without referencing its source paper).
*   **Leaky Abstractions:** Database queries or HTTP requests written directly inside mathematical domain functions.

---

## 4. Principle Verification Checklist

### 4.1 Scientific Integrity Checks
*   [ ] Does the output show statistical ranges, or is it a point estimate?
*   [ ] Are all inputs mapped to database parameters with documented citations?
*   [ ] If a constant was updated, does it link to a verified BibTeX reference?

### 4.2 Code Design Checks
*   [ ] Are the core mathematical modules free from database or network imports?
*   [ ] Are all random number generators explicitly seeded?
*   [ ] Does the test coverage for the modified domain code exceed $95\%$?
*   [ ] Did the execution time stay within performance budgets?

---

## 5. Glossary

*   **Hexagonal Architecture:** A structural pattern separating the core business domain logic from external infrastructure inputs/outputs (ports and adapters).
*   **Row-Level Security (RLS):** Database policies that restrict rows returned in queries to matching tenant identifiers.
*   **Sobol Indices:** A variance-based sensitivity analysis method evaluating how parameter uncertainty impacts output variance.
*   **Stiff ODE:** A system of ordinary differential equations containing widely differing rate timescales, requiring specialized implicit integration methods (like BDF).

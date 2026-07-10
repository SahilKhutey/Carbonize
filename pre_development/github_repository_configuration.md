# 🐙 GitHub Repository: Complete Setup & Configuration

This document specifies the Git branching strategy, automated GitHub Actions workflows, issue templates, PR templates, and community health files configured for the **Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator (CBMS-Sim)**.

---

## 1. Repository Directory Structure Manifest

All GitHub configuration files are located in the project's root under the `.github/` folder:

```
.github/
├── workflows/
│   ├── ci.yml                 # Continuous Integration test runner
│   ├── release.yml            # Semantic release tag compiler
│   └── nightly.yml            # Nightly performance & regression tests
├── ISSUE_TEMPLATE/
│   ├── bug_report.md          # Bug report structure
│   ├── feature_request.md     # Feature request form
│   └── security.md            # Security report instructions
├── PULL_REQUEST_TEMPLATE.md   # Standard pull request description checklist
├── CODEOWNERS                 # File-level maintainer maps
├── dependabot.yml             # Weekly Python/npm dependency updates
└── SECURITY.md                # Vulnerability disclosure safe harbor policy
```

---

## 2. CI/CD GitHub Actions Workflows

### 2.1 Main CI Pipeline (`ci.yml`)
*   **Trigger:** Runs on any push to `main`, `develop`, `release/*`, or PR updates.
*   **Lint & Formatting:** Runs Ruff and Black checks.
*   **Static Analysis:** Performs mypy type checks.
*   **Calculations & Solver Tests:** Fires `pytest` checking the ODE kinetics and mass balances.
*   **Frontend Tests:** Runs Jest/Vitest suite and bundles React production assets.

### 2.2 Dependabot Scanning (`dependabot.yml`)
*   **Schedule:** Runs weekly on Monday mornings.
*   **Scope:** Scopes Python dependencies (Poetry `pyproject.toml`) and Node modules (pnpm workspace) for vulnerability alerts and bumps.

---

## 3. Branch Protection Rules

The default branch `main` is protected with the following requirements:
*   **Pull Request Checks:** Requires a minimum of 2 approving reviews from Code Owners before merge.
*   **Linear History:** Squashes commits on merge to keep history linear.
*   **Status Verifications:** Blocks merges unless the following pipeline checks pass:
    *   `Backend CI / Lint & Format`
    *   `Backend CI / Test`
    *   `Frontend CI / Test`
    *   `Security Scan / CodeQL`

---

## 4. Community Health & Security Policies

### 4.1 CODEOWNERS Map
Assigns explicit code maintainership over sensitive components:
*   `/packages/sim-core/`: `@cbms/sim-core-maintainers`
*   `/packages/api/`: `@cbms/api-maintainers`
*   `/packages/web/`: `@cbms/web-maintainers`
*   `/.github/`: `@cbms/devops-team`

### 4.2 Security Vulnerability Policy (`SECURITY.md`)
*   **Disclosure:** Encourages private reporting via GitHub Advisories or emailing `security@cbms.in`.
*   **Safe Harbor:** Affords legal protections for security researchers who act in good faith.

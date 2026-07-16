# Contributing to CBMS-Sim

Thank you for your interest in contributing to the Coral-Inspired Biomineralization Multi-Pollutant Capture Simulator (CBMS-Sim). This document explains how to contribute effectively.

---

## 📋 Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Pull Request Process](#pull-request-process)
5. [Coding Standards](#coding-standards)
6. [Testing Requirements](#testing-requirements)
7. [Documentation Standards](#documentation-standards)
8. [Scientific Contributions](#scientific-contributions)
9. [Security Disclosures](#security-disclosures)
10. [Getting Help](#getting-help)

---

## 📜 Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Report unacceptable behavior to `conduct@cbms.in`.

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Core simulation engine |
| Poetry | 1.8+ | Python dependency management |
| Node.js | 20+ | Frontend (TypeScript/React) |
| pnpm | 9+ | Node package management |
| Docker | 24+ | Local services (Postgres, Redis) |
| Git | 2.40+ | Version control |

### One-Time Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/cbms-platform.git
cd cbms-platform

# 2. Install Python dependencies
poetry install

# 3. Install pre-commit hooks (REQUIRED)
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg

# 4. Install Node dependencies
cd packages/web
pnpm install
cd ../..

# 5. Start local services
docker compose -f .devcontainer/docker-compose.yml up -d

# 6. Initialize database
poetry run python scripts/setup_db.py
poetry run python scripts/seed_data.py

# 7. Warm up Numba kernels (one-time, ~30s)
poetry run python scripts/warmup.py

# 8. Verify setup
make ci-lint
make test
```

### Alternative: GitHub Codespaces (Recommended for New Contributors)
Click the "Code" button → "Codespaces" → "Create codespace". The full environment boots in ~3 minutes.

---

## 🔄 Development Workflow

### Branch Strategy
| Branch | Purpose | Protection |
| :--- | :--- | :--- |
| `main` | Production-ready code | 🔒 Protected: 2 reviews, CI required |
| `develop` | Integration branch for next release | 🟡 CI required |
| `feature/*` | New features | 🟢 Standard PR review |
| `fix/*` | Bug fixes | 🟢 Standard PR review |
| `docs/*` | Documentation only | 🟢 Standard PR review |
| `release/*` | Release preparation | 🔒 Protected: 1 review |
| `hotfix/*` | Urgent production fixes | 🔒 Expedited review |

### Typical Workflow
```bash
# 1. Create a feature branch from develop
git checkout develop
git pull origin develop
git checkout -b feature/add-sobol-sensitivity

# 2. Make changes, commit frequently
git add .
git commit -m "feat(uq): add Sobol sensitivity analysis

- Implement Saltelli sampling scheme
- Compute first and total order indices
- Add critical experiments recommender
- Include 4 canonical validation cases

Closes #123"

# 3. Push and open PR
git push origin feature/add-sobol-sensitivity
gh pr create --base develop --title "feat(uq): add Sobol sensitivity"

# 4. Address review feedback
git add .
git commit -m "fix(uq): address review comments - improve docstrings"
git push

# 5. After approval, squash-merge
gh pr merge --squash --delete-branch
```

### Commit Message Format
We use Conventional Commits:
`<type>(<scope>): <subject>`

`<body>`

`<footer>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`

*Example:*
```
feat(kinetics): add thermostable CA variant
fix(api): correct rate limit calculation
docs(architecture): update ADRs with v0.3 decisions
test(workers): add chaos tests for Redis failures
ci: add CodeQL scanning to PR pipeline
```

---

## 🔀 Pull Request Process

### Before Opening a PR
Complete this checklist:
*   Code follows the Coding Standards.
*   All tests pass locally: `make test`
*   Linting passes: `make lint`
*   Type checking passes: `make type-check`
*   Test coverage $\ge 80\%$: `make test-coverage`
*   Pre-commit hooks pass: `poetry run pre-commit run --all-files`
*   Documentation updated (if user-facing change).
*   `CHANGELOG.md` updated.
*   No new security warnings.
*   Linked to an issue (if applicable).
*   Sign the Contributor License Agreement (CLA) (required for all new contributors).

### PR Template
We provide a PR template (`.github/PULL_REQUEST_TEMPLATE.md`). Fill out all sections.

### Contributor License Agreement (CLA)
All contributors must sign our Contributor License Agreement before their pull requests can be merged. 
*   **How it works:** When you open your first pull request, our automated CLA Assistant bot will analyze the PR and comment with a link to sign. 
*   **Sign-off:** Follow the link, authorize with GitHub, and sign the CLA. Future pull requests will be approved automatically.

### Review Process
*   Automated checks must pass (CI pipeline).
*   CODEOWNERS auto-assigns reviewers based on changed files.
*   2 approvals required for `main` (1 for feature branches).
*   All conversations must be resolved.
*   No requested changes outstanding.
*   Branch is up-to-date with base.
*   Squash-merge is the default merge strategy.

### After Merge
*   Your branch is automatically deleted.
*   CI runs on `main` to verify post-merge health.
*   Deployment to staging is triggered automatically.
*   Your contribution appears in the next release notes.

---

## 📏 Coding Standards

### Python Style
We enforce these via ruff, black, isort, and mypy:
*   **ruff**: Linting (`pyproject.toml [tool.ruff]`)
*   **black**: Formatting (line length 100) (`pyproject.toml [tool.black]`)
*   **isort**: Import sorting (`pyproject.toml [tool.isort]`)
*   **mypy**: Static type checking (`pyproject.toml [tool.mypy]` strict mode)

Type Hints (REQUIRED):
```python
from typing import Optional
from decimal import Decimal

def compute_capture_efficiency(
    co2_input_kg_hr: float,
    co2_output_kg_hr: float,
    tolerance: Optional[Decimal] = None,
) -> CaptureResult:
    """Compute CO₂ capture efficiency.
    
    Args:
        co2_input_kg_hr: Input CO₂ mass flow rate (kg/hr).
        co2_output_kg_hr: Output CO₂ mass flow rate (kg/hr).
        tolerance: Optional tolerance for mass balance (default: 0.5%).
    
    Returns:
        CaptureResult with efficiency percentage and metadata.
    
    Raises:
        ValueError: If inputs are negative.
    """
    if co2_input_kg_hr <= 0:
        raise ValueError("co2_input_kg_hr must be positive")
    
    captured = co2_input_kg_hr - co2_output_kg_hr
    return CaptureResult(
        efficiency_pct=(captured / co2_input_kg_hr) * 100,
        captured_kg_hr=captured,
    )
```

### TypeScript Style
We enforce these via eslint and prettier:
*   **eslint**: Linting with `@typescript-eslint/recommended`
*   **prettier**: Formatting (line length 100, single quotes)
*   **tsc**: Type checking (strict mode)

React Component Style:
```tsx
import { useState } from 'react';
import { Button } from '@/components/ui/Button';

interface SimulationFormProps {
  plantId: string;
  onSubmit: (config: SimulationConfig) => Promise<void>;
}

export function SimulationForm({ plantId, onSubmit }: SimulationFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit({ plantId });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Button type="submit" loading={isSubmitting}>
        Run Simulation
      </Button>
    </form>
  );
}
```

### File Organization
```
packages/
├── sim-core/          # Pure scientific logic (no I/O)
│   └── src/cbms_sim/
│       ├── domain/    # Business entities, rules
│       ├── application/  # Use cases, services
│       └── infrastructure/  # Adapters to external systems
├── api/               # FastAPI HTTP/WebSocket layer
├── workers/           # Celery async task workers
├── cfd/               # OpenFOAM integration
├── web/               # React frontend
└── shared/            # Cross-cutting utilities
```

---

## 🧪 Testing Requirements

### Coverage Targets
| Package | Minimum Coverage | Target Coverage |
| :--- | :--- | :--- |
| `sim-core/domain/` | 90% | 95% |
| `sim-core/application/` | 80% | 90% |
| `api/` | 75% | 85% |
| `workers/` | 70% | 80% |
| `web/components/` | 70% | 80% |
| `web/features/` | 75% | 85% |
| **Overall** | **80%** | **85%** |

### Test Types
*   **Unit**: Tested with `pytest` for unit logic.
*   **Property**: Tested with `hypothesis` for core invariants (e.g. mass balance).
*   **Integration**: Tested with `pytest` + Docker for API/DB boundaries.
*   **Contract**: Tested with `schemathesis` to ensure OpenAPI specs are honored.
*   **Architecture**: Tested with `pytest` + AST to enforce layer boundaries.
*   **Security**: Scanned with `bandit` + manual testing.
*   **Chaos**: Tested with `chaos-mesh` weekly for resilience.
*   **E2E**: Executed with `playwright` before major releases.
*   **Performance**: Benchmarked with `pytest-benchmark` nightly.

### Running Tests
```bash
# All tests
make test
# Unit only
make test-unit
# With coverage
make test-coverage
```

---

## 📚 Documentation Standards

### Code Documentation
*   All public functions must have docstrings (Google style for Python, JSDoc for TypeScript).
*   Module-level docstrings are required for non-trivial files.
*   Complex algorithms must include inline comments explaining the "why".
*   Magic numbers must be named constants with documented sources.

### User Documentation
*   Update the relevant page in `docs/`.
*   Add an entry to `CHANGELOG.md`.
*   If it's a major feature, create a tutorial under `docs/tutorials/`.

### Architecture Documentation
*   Create an ADR in `docs/adr/` using the template.
*   Number sequentially (e.g., `0014-sobol-analysis.md`).

---

## 🔬 Scientific Contributions

### Parameter Changes
If you modify any parameter in `data/parameters/v2026.1.json`:
1.  Cite the source (DOI, paper, or experiment ID).
2.  Justify the change in the PR description.
3.  Update validation cases if affected.
4.  Request review from `@cbms/science-team`.

### Model Changes
If you modify the core reaction kinetics:
1.  Add a validation case demonstrating the model still matches published data.
2.  Document the change in `manuscript/theory/kinetics.md`.
3.  Run the full validation suite: `make validate`.

### New Reactions
If you add a new chemical reaction:
1.  Include stoichiometry, rate law, and parameter source.
2.  Add unit and integration tests.
3.  Add the new reaction to the 9-species ODE state vector.

---

## 🔒 Security Disclosures

Do NOT open public issues for security vulnerabilities.
*   **GitHub Security Advisories (preferred)**: Security tab $\to$ "Report a vulnerability".
*   **Email**: `security@cbms.in` (PGP key in `SECURITY.md`).
*   *Response time:* 48 hours for initial acknowledgment, 7 days for critical fixes.

---

## 🆘 Getting Help

### Where to Ask
*   **How do I...?**: Read this document + files in `docs/`.
*   **I'm stuck on...**: Open a discussion under GitHub Discussions.
*   **I found a bug / have an idea**: Create a GitHub Issue.
*   **Security issue**: Contact `security@cbms.in`.
*   **Code of Conduct violation**: Contact `conduct@cbms.in`.

### Discussion Categories
*   `General`: Questions about usage.
*   `Ideas`: Feature suggestions before creating an issue.
*   `Q&A`: Help with setup.
*   `Research`: Scientific discussions, parameter validation.

### Response Times
*   Critical security: 48 hours
*   Bug report: 2 business days
*   Feature request: 1 week
*   PR review: 1–2 business days

---

## 🔄 PR Lifecycle Policy

### PR States
| State | Definition | Action |
| :--- | :--- | :--- |
| **Draft** | Work in progress, not ready for review | Author keeps working |
| **Open - Awaiting Review** | Ready for review, CI green | CODEOWNERS auto-assigned |
| **Open - Changes Requested** | Reviewer has feedback | Author addresses comments |
| **Open - Approved** | All approvals received | Ready to merge |
| **Stale (30+ days)** | No activity for 30 days | Auto-reminder sent, auto-close at 60 days |
| **Closed - Merged** | Successfully merged | Branch deleted |
| **Closed - Stale** | Abandoned or obsolete | Branch preserved 90 days, then deleted |

### Service Level Agreements (SLAs)
*   **First review response**: 2 business days
*   **Subsequent reviews**: 1 business day
*   **Merge after approval**: Within 24 hours
*   **Stale PR closure**: 30 days of inactivity $\to$ reminder; 60 days $\to$ close
*   **CI duration**: < 10 minutes
*   **Total PR lifecycle**: < 7 days target

---

## 🪝 Pre-Commit Hooks (Required)

We use [pre-commit](https://pre-commit.com/) to enforce code quality on every commit. **All contributors must install the hooks.**

### One-Time Setup

```bash
# Install pre-commit (via Poetry)
poetry add --group dev pre-commit

# Install the git hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
poetry run pre-commit install --hook-type pre-push

# Generate secrets baseline (first time only)
poetry run detect-secrets scan > .secrets.baseline

# Run on all files to verify setup
poetry run pre-commit run --all-files
```

### What Gets Checked
Every commit triggers these checks:

| Tool | What It Does | Auto-Fix? |
|------|--------------|-----------|
| **pre-commit-hooks** | Trailing whitespace, file size, line endings | ✅ Yes |
| **detect-secrets** | Prevents API keys/passwords from being committed | ❌ No (blocks) |
| **ruff** | Fast Python linter (style, bugs, imports) | ✅ Yes |
| **black** | Python code formatter | ✅ Yes |
| **isort** | Python import sorting | ✅ Yes |
| **mypy** | Python type checking (non-strict mode) | ❌ No |
| **bandit** | Python security linter | ❌ No |
| **eslint** | TypeScript/React linter | ❌ No (warns) |
| **prettier** | TypeScript/React formatter | ✅ Yes |
| **tsc** | TypeScript type checking | ❌ No |
| **markdownlint** | Markdown style | ✅ Yes |
| **shellcheck** | Shell script linter | ❌ No |
| **hadolint** | Dockerfile linter | ❌ No |
| **actionlint** | GitHub Actions linter | ❌ No |

### Typical Workflow
```bash
# Make changes
git add .
git commit -m "feat(kinetics): add CA variant"

# Pre-commit runs automatically
# If fixes are applied:
git add .  # Stage the auto-fixed files
git commit -m "feat(kinetics): add CA variant"

# If checks fail and can't auto-fix:
# Fix manually based on error message, then commit again
```

### Bypassing Hooks (Use Sparingly!)
```bash
# Skip all hooks (for emergency WIP)
git commit --no-verify -m "wip: ..."

# Skip specific hook
SKIP=mypy git commit -m "..."
```
Never bypass `detect-secrets`, `bandit`, or `check-added-large-files`.

---

## 🙏 Thank You
Every contribution matters. We appreciate your time and effort to make CBMS-Sim better!

*Last updated: February 2025.*

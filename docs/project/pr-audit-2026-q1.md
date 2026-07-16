# PR Audit — Open Pull Requests Review & Cleanup

**Audit Date:** Q1 2026  
**PR Audit Lead:** Project Team Lead (PTL)  
**Scope:** All 6 open PRs in `cbms/platform`  
**Objective:** Close stale, rebase outdated, document what remains in flight  

---

## 🎯 Audit Summary

| Metric | Value |
| :--- | :--- |
| **PRs Audited** | 6 |
| **Closed (stale/abandoned)** | 2 |
| **Rebased** | 1 |
| **Remaining in Flight** | 3 |
| **Action Required** | See table below |

**Outcome:** 2 stale PRs closed, 1 rebased onto main, 3 confirmed active and in flight. PR backlog reduced from 6 $\to$ 3.

---

## 📊 Open PRs — Initial State

| # | PR # | Title | Author | Age | Status Before | Action Taken |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | #42 | WIP: Add carbonic anhydrase kinetics module | @dev-alice | 47 days | Draft, no activity 30+ days | ❌ Closed (stale) |
| **2** | #45 | feat(sensitivity): implement Sobol first-order indices | @dev-bob | 23 days | Needs rebase, 8 conflicts | 🔄 Rebased |
| **3** | #47 | fix(workers): handle Redis disconnection gracefully | @dev-carol | 12 days | Active, CI green | ✅ Keep open |
| **4** | #48 | docs: add CCTS compliance methodology | @dev-david | 19 days | Active, awaiting review | ✅ Keep open |
| **5** | #51 | chore(deps): bump fastapi 0.115.0 $\to$ 0.115.4 | @dependabot | 5 days | Dependabot auto-PR | ✅ Keep open |
| **6** | #53 | feat(uq): add inverse Gaussian FPT distribution | @dev-eve | 3 days | Active, CI green | ✅ Merged |

---

## 🔍 Detailed Audit Findings

### PR #42 — ❌ Closed (Stale)
*   **Title:** WIP: Add carbonic anhydrase kinetics module
*   **Author:** @dev-alice
*   **Branch:** `feature/ca-kinetics` $\to$ `main`
*   **CI:** Failing (type errors)
*   **Why stale?** Author is unavailable. Work overlaps with PR #45 (Sobol). Code coverage is $<40\%$.
*   **Action Taken:** Closed as stale. Created issue #89 to re-scope this work.

### PR #45 — 🔄 Rebased
*   **Title:** feat(sensitivity): implement Sobol first-order indices
*   **Author:** @dev-bob
*   **Branch:** `feature/sobol-first-order` $\to$ `develop`
*   **Conflicts resolved:** Added new exports in `__init__.py`, sorted pyproject.toml dependencies, and resolved test conftest conflicts. Rebased onto develop and force-pushed.
*   **Review Comments Addressed:**
    1.  Added Saltelli sampling scheme (`saltelli_sample()`).
    2.  Added property test for non-negativity of Sobol indices.

### PR #47 — ✅ Keep Open (Active)
*   **Title:** fix(workers): handle Redis disconnection gracefully
*   **Author:** @dev-carol
*   **Branch:** `fix/redis-disconnect` $\to$ `develop`
*   **Why active?** Handles worker disconnection incident #INC-2025-08. Integration test added. Awaiting 1 more approval.

### PR #48 — ✅ Keep Open (Awaiting Review)
*   **Title:** docs: add CCTS compliance methodology
*   **Author:** @dev-david
*   **Branch:** `docs/ccts-methodology` $\to$ `main`
*   **Why active?** Required for CCTS BEE methodology submission by March 15. Reviewers need to review glossary added in commit `b4f7c92`.

### PR #51 — ✅ Keep Open (Dependabot)
*   **Title:** chore(deps): bump fastapi 0.115.0 $\to$ 0.115.4
*   **Author:** @dependabot[bot]
*   **Branch:** `dependabot/pip/fastapi-0.115.4` $\to$ `develop`
*   **Why active?** Routine dependency bump. Enable auto-merge command triggered.

### PR #53 — ✅ Merged
*   **Title:** feat(uq): add inverse Gaussian FPT distribution
*   **Author:** @dev-eve
*   **Branch:** `feature/inverse-gaussian-fpt` $\to$ `develop`
*   **Action Taken:** Merged into `develop` as all CI checks were green and research lead approved.

---

## 🧹 Branch Cleanup

*   `feature/inverse-gaussian-fpt`: Merged via PR #53 $\to$ **Deleted**
*   `feature/ca-kinetics`: Closed, preserved 90 days $\to$ **Will delete after 90 days**
*   `dependabot/pip/fastapi-0.115.4`: Will auto-delete after merge.

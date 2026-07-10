# 🔧 Simulation Software Engineering Principles & Guidelines: CBMS-Sim Engineering Handbook

This document defines the engineering guidelines, coding standards, and best practices that govern every contribution in the **Coral-Inspired Biomineralization Simulator (CBMS-Sim)**.

---

## 1. Engineering Philosophy Statement

### 1.1 The CBMS-Sim Engineering Creed
We build scientific software for industrial deployment. Our code must be **correct first, fast second, and clear always**.

### 1.2 Core Engineering Values
*   **Correctness:** Scientific accuracy (mass conservation, physical bounds) is non-negotiable.
*   **Clarity:** Write clean code that can be easily parsed by the next developer.
*   **Consistency:** Follow uniform naming conventions, module structures, and testing patterns.

---

## 2. Python Coding Standards

### 2.1 Style & Formatting
*   **Linting:** Enforce PEP 8 conventions using `ruff`.
*   **Formatting:** Use `black` with a default line-length of 100 characters.
*   **Imports:** Sort imports using `isort` configured with the black profile.

### 2.2 Naming Conventions
*   **Modules:** `snake_case` (e.g., `uncertainty_engine.py`).
*   **Classes:** `PascalCase` (e.g., `SimulationSolver`).
*   **Functions & Variables:** `snake_case` (e.g., `compute_capture_efficiency`, `co2_concentration`).
*   **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_REACTION_STEPS`).

---

## 3. Type Hints & Static Typing

*   **Strict Typings:** All function signatures must contain complete type annotations.
*   **Optional Values:** Use `Optional[T]` or `Union[T, None]` to denote nullable types.
*   **Pydantic Integration:** Use Pydantic v2 schemas at all API input validation entry points, forbidding extra fields (`extra="forbid"`).

---

## 4. Error Handling Patterns

*   **Exceptions:** Define typed subclasses of `CBMSError`. Avoid throwing generic `Exception` or `RuntimeError`.
*   **Resource Cleanup:** Always use `with` blocks or `finally` clauses to release files, database transactions, or Redis connections.
*   **No Silent Failures:** Never use empty `except:` catches. Log warning/error levels with structlog if an operation fails.

---

## 5. Performance Engineering

*   **Measurement First:** Profile bottlenecks using `cProfile` before performing code optimizations.
*   **Optimization Pipeline:**
    ```
    1. Measure (Profile) -> 2. Identify Bottleneck -> 3. Optimize (Numba/Vectorize) -> 4. Verify (Benchmark)
    ```
*   **JIT Compilation:** Wrap inner-loop mathematical models in Numba JIT compiling (`@njit(cache=True)`) to run loops at near-C speeds.

---

## 6. Definition of Done (DoD)

A task is considered complete and ready to merge only when:
*   [ ] All tests in the pipeline pass successfully.
*   [ ] Test coverage remains above $80\%$ overall ($95\%$ for domain mathematical core).
*   [ ] Docstrings conform to the Google standard.
*   [ ] Linting and formatting checks pass without warning.
*   [ ] The walkthrough has been updated.

## Description
Briefly describe the purpose of this PR (what changes are introduced, why they are needed, and how they resolve issues/roadmaps).

## Related Issues
Closes # (issue number)

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Scientific update (changes to kinetic solver, UQ, parameters, or validation cases)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] DevOps/Hygiene/CI change

## 🎯 Definition of Done (DoD) Checklist
Please verify that your PR meets all of the following requirements before requesting review:

- [ ] **Formatting**: Code follows project style guides (Ruff/Black for Python, Prettier/ESLint for TypeScript).
- [ ] **Type Hints**: Strict type hints are complete (`mypy --strict` passes in Python, TypeScript compilation passes).
- [ ] **Tests**: Unit tests are added/updated with at least 80% coverage on new code.
- [ ] **Scientific Validation**: Validations run and pass within the specified tolerances (run `make validate` or `python -m cbms_sim.validation.run`).
- [ ] **Documentation**: README, code docstrings (Google style for Python), and docs are updated.
- [ ] **ADR**: Architectural Decision Record created/updated if applicable.
- [ ] **CI Checks**: GitHub Action checks are green.
- [ ] **Reviews**: Approved by designated CODEOWNERS.

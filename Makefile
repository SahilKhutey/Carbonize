# =============================================================================
# CBMS-Sim Platform Makefile
# =============================================================================

.PHONY: help pre-commit-install pre-commit-run pre-commit-update pre-commit-clean test

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# =============================================================================
# Pre-Commit Hooks
# =============================================================================

pre-commit-install: ## Install pre-commit hooks
	poetry run pre-commit install
	poetry run pre-commit install --hook-type commit-msg
	poetry run pre-commit install --hook-type pre-push
	@echo "✅ Pre-commit hooks installed"

pre-commit-run: ## Run pre-commit on all files
	poetry run pre-commit run --all-files

pre-commit-update: ## Update pre-commit hook versions
	poetry run pre-commit autoupdate

pre-commit-clean: ## Clean pre-commit cache
	poetry run pre-commit clean

test: ## Run tests
	python -m pytest

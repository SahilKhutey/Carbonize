#!/bin/bash
# =============================================================================
# Pre-Commit Setup Script
# =============================================================================
# Installs pre-commit, configures secrets baseline, verifies installation.
# Run once after cloning the repository.
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ----------------------------------------------------------------------------
# Helper functions
# ----------------------------------------------------------------------------
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# ----------------------------------------------------------------------------
# 1. Check prerequisites
# ----------------------------------------------------------------------------
print_header "Step 1: Checking Prerequisites"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.12+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Check pip
if ! command -v pip &> /dev/null; then
    print_error "pip not found. Please install pip"
    exit 1
fi
print_success "pip found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js not found. Please install Node.js 20+"
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION found"

# Check pnpm
if ! command -v pnpm &> /dev/null; then
    print_warning "pnpm not found. Installing..."
    npm install -g pnpm@9
    print_success "pnpm installed"
fi
PNPM_VERSION=$(pnpm --version)
print_success "pnpm $PNPM_VERSION found"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    print_warning "Poetry not found. Installing..."
    curl -sSL https://install.python-poetry.org | python3 -
    print_success "Poetry installed"
fi
POETRY_VERSION=$(poetry --version)
print_success "$POETRY_VERSION found"

# ----------------------------------------------------------------------------
# 2. Install pre-commit
# ----------------------------------------------------------------------------
print_header "Step 2: Installing Pre-Commit"

# Install via Poetry (project-level)
poetry add --group dev pre-commit

# Verify installation
poetry run pre-commit --version
print_success "pre-commit installed"

# ----------------------------------------------------------------------------
# 3. Generate secrets baseline
# ----------------------------------------------------------------------------
print_header "Step 3: Generating Secrets Baseline"

if [ ! -f ".secrets.baseline" ]; then
    print_warning "No secrets baseline found. Generating..."
    poetry run detect-secrets scan > .secrets.baseline
    print_success "Secrets baseline created"
else
    print_success "Secrets baseline already exists"
fi

# Audit the baseline (only if explicitly requested)
if [ "${AUDIT_SECRETS:-false}" = "true" ]; then
    poetry run detect-secrets audit .secrets.baseline
fi

# ----------------------------------------------------------------------------
# 4. Install git hooks
# ----------------------------------------------------------------------------
print_header "Step 4: Installing Git Hooks"

# Install pre-commit hook
poetry run pre-commit install

# Install commit-msg hook (for conventional commit validation)
poetry run pre-commit install --hook-type commit-msg

# Install pre-push hook (for more thorough checks)
poetry run pre-commit install --hook-type pre-push

print_success "Git hooks installed"

# Verify hook installation
if [ -f ".git/hooks/pre-commit" ]; then
    print_success "pre-commit hook installed at .git/hooks/pre-commit"
fi

# ----------------------------------------------------------------------------
# 5. Run initial scan
# ----------------------------------------------------------------------------
print_header "Step 5: Running Initial Scan (this may take a while)"

# Run on all files to check current state
if poetry run pre-commit run --all-files; then
    print_success "All checks passed!"
else
    print_warning "Some checks failed. This is normal for initial setup."
    print_warning "Pre-commit has automatically fixed many issues."
    print_warning "Review changes and commit them: git add -A && git commit -m 'chore: apply pre-commit fixes'"
fi

# ----------------------------------------------------------------------------
# 6. Install Node dependencies for frontend hooks
# ----------------------------------------------------------------------------
print_header "Step 6: Installing Frontend Hook Dependencies"

cd packages/web
pnpm install
cd ../..

print_success "Frontend dependencies installed"

# ----------------------------------------------------------------------------
# 7. Verify setup
# ----------------------------------------------------------------------------
print_header "Step 7: Verification"

echo "Checking pre-commit version..."
poetry run pre-commit --version

echo ""
echo "Checking installed hooks..."
poetry run pre-commit run --all-files --verbose 2>&1 | head -20

echo ""
echo "Checking git hook permissions..."
ls -la .git/hooks/pre-commit .git/hooks/commit-msg .git/hooks/pre-push 2>/dev/null

# ----------------------------------------------------------------------------
# Summary
# ----------------------------------------------------------------------------
print_header "✅ Pre-Commit Setup Complete"

cat << 'EOF'

🎉 Pre-commit is now installed and configured!

What happens now:
  • Every `git commit` will trigger automated checks
  • If checks fail, the commit is blocked
  • Many issues are auto-fixed (formatting, trailing whitespace, etc.)
  • You may need to `git add` the auto-fixed files and commit again

Common commands:
  poetry run pre-commit run --all-files    # Run on all files
  poetry run pre-commit run <hook-id>     # Run specific hook
  poetry run pre-commit autoupdate         # Update hook versions
  git commit --no-verify                  # Skip hooks (use sparingly!)

Bypass only for:
  • WIP commits (but fix before pushing)
  • Emergency hotfixes (mention in commit message)
  • Never bypass security hooks (secrets, bandit)

Need help? See: docs/development/pre-commit.md

EOF

#!/bin/bash
# Test PyPI installation of wiggum
# This script creates an isolated environment and tests the package from PyPI
#
# Usage: ./scripts/test-pypi-install.sh [version]
#   version: optional, defaults to latest (e.g., "0.1.3" or "wiggum==0.1.3")
#
# Requirements: uv must be installed

set -e

VERSION=${1:-"wiggum"}
if [[ "$VERSION" != wiggum* ]]; then
    VERSION="wiggum==$VERSION"
fi

TEST_DIR=$(mktemp -d)
echo "Testing $VERSION in $TEST_DIR"

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

cd "$TEST_DIR"

# Create and activate virtual environment
uv venv --quiet
source .venv/bin/activate

# Install wiggum from PyPI
echo "Installing $VERSION..."
uv pip install "$VERSION" --quiet

# Test 1: CLI is available
echo -n "Test 1: CLI available... "
if wiggum --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

# Test 2: All commands have help
echo -n "Test 2: run --help... "
if wiggum run --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

echo -n "Test 3: init --help... "
if wiggum init --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

echo -n "Test 4: add --help... "
if wiggum add --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

# Test 5: add command creates TASKS.md
echo -n "Test 5: add command works... "
wiggum add "Test task from PyPI install" > /dev/null
if [[ -f "TASKS.md" ]] && grep -q "Test task from PyPI install" TASKS.md; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

# Test 6: run --dry-run without LOOP-PROMPT.md fails appropriately
echo -n "Test 6: run fails without LOOP-PROMPT.md... "
if ! wiggum run --dry-run 2>&1 | grep -q "not found"; then
    echo "FAIL (expected error about missing file)"
    exit 1
fi
echo "PASS"

# Test 7: run --dry-run with LOOP-PROMPT.md works
echo -n "Test 7: run --dry-run works... "
echo "# Test Prompt" > LOOP-PROMPT.md
if wiggum run --dry-run 2>&1 | grep -q "Would run"; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

echo ""
echo "All tests passed!"
echo "Tested version: $(uv pip show wiggum 2>/dev/null | grep Version)"

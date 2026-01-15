#!/bin/bash
# Quick PyPI test using uvx (no venv needed)
# Usage: ./scripts/test-pypi-quick.sh

set -e

echo "Quick PyPI test using uvx..."

echo -n "Test 1: uvx wiggum --help... "
if uvx wiggum --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

echo -n "Test 2: uvx wiggum run --help... "
if uvx wiggum run --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

echo -n "Test 3: uvx wiggum init --help... "
if uvx wiggum init --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

echo -n "Test 4: uvx wiggum add --help... "
if uvx wiggum add --help > /dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL"
    exit 1
fi

echo ""
echo "All quick tests passed!"

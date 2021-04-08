#!/bin/bash
set -euo pipefail

isort --profile black --diff --check-only boxkite tests
black --check boxkite tests

pytest -svl --log-level=DEBUG --color=yes --cov=boxkite --cov-fail-under=90 --cov-report=xml tests

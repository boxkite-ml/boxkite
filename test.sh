#!/bin/bash

isort --profile black --diff --check-only boxkite tests
black --check boxkite tests

pytest -svl --log-level=DEBUG --color=yes --cov=boxkite --cov-fail-under=90 --cov-report=html --cov-report=xml tests
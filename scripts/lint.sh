#!/usr/bin/env bash

set -euxo pipefail

isort --check-only .
black --check --diff .
flake8 --jobs 4 --statistics --show-source --config ./setup.cfg .
mypy --config-file ./setup.cfg .

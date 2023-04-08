#!/usr/bin/env bash

set -euxo pipefail

isort --check-only --settings-path=./setup.cfg .
black --check --diff .
flake8 --jobs 4 --statistics --show-source --config ./setup.cfg .
mypy --config-file ./setup.cfg .

#!/usr/bin/env bash

set -euxo pipefail

pytest --cov=app --cov-report=term --cov-config=./setup.cfg .

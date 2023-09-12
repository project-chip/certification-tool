#!/usr/bin/env bash

set -x

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"


poetry run mypy app/main.py
poetry run black app
poetry run isort app
poetry run flake8

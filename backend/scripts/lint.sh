#!/usr/bin/env bash

set -x

mypy app test_collections
black app test_collections --check
isort --check-only app test_collections
flake8
cspell "" --no-progress
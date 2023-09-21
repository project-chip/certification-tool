#! /usr/bin/env bash

set -e

# Prevent automatic path conversions by MSYS-based bash. 
# It's revelant only for Windows
export MSYS_NO_PATHCONV=1 

PACKAGE_NAME=api_lib_autogen
OUTPUT_DIR="app"
PACKAGE_PATH=$OUTPUT_DIR/$PACKAGE_NAME

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && cd .. && pwd)"
rm -r $PACKAGE_PATH || true
./client_generator/scripts/generate.sh -i ./openapi.json -p $PACKAGE_NAME -o $OUTPUT_DIR
poetry run mypy ./$PACKAGE_PATH
poetry run black ./$PACKAGE_PATH
poetry run flake8 ./$PACKAGE_PATH
poetry run isort ./$PACKAGE_PATH
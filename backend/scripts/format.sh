#!/bin/sh -e
set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app test_collections --exclude=__init__.py
black app test_collections
isort app test_collections

#!/bin/sh -e
set -x

isort --recursive --apply app
sh ./scripts/format.sh

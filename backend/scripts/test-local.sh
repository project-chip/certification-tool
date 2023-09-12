#!/usr/bin/env bash

set -e
set -x

#!/bin/sh
for arg in "$@"
do
    case $arg in
        --run-platform-dependant)
        RUN_ALL_TESTS=1
        shift # Remove --run-all from processing
        ;;
        *)
        OTHER_ARGUMENTS+=("$1")
        shift # Remove generic argument from processing
        ;;
    esac
done

if [[ $RUN_ALL_TESTS -eq 1 ]]
then
    echo "Running all tests"
    pytest --cov-config=.coveragerc --cov=app --cov=test_collections --cov-report=term-missing app/tests "${@}"
else
    echo "Skipping platform dependant tests"
    pytest --cov-config=.coveragerc --cov=app --cov=test_collections --cov-report=term-missing --ignore=app/tests/platform_dependent_tests app/tests "${@}"
fi

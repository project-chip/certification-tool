#! /usr/bin/env bash
set -e

# Set PYTHONPATH so python modules can import `app`
ROOT_DIR=$(realpath $(dirname "$0"))
export PYTHONPATH="${PYTHONPATH}:$ROOT_DIR"

# Loop through arguments and process them
# -r or --reset-db will be passed to the app/tests/tests_pre_start.py
for arg in "$@"
do
    case $arg in
        -r|--reset-db)
        SHOULD_RESET_DB=1
        shift # Remove --reset-db from processing
        ;;
        *)
        OTHER_ARGUMENTS+=("$1")
        shift # Remove generic argument from processing
        ;;
    esac
done


if [[ $SHOULD_RESET_DB -eq 1 ]]
then
    PRE_START_ARG="--reset-db"
fi


python ./app/tests/tests_pre_start.py "$PRE_START_ARG"
bash ./scripts/test-local.sh "$OTHER_ARGUMENTS"

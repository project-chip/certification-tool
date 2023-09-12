#!/bin/bash -e
set -x
set -e


# Usage: ./scripts/fetch_sdk_yaml_tests.sh [sdk path]
# 
# When an SDK path is supplied, the SDK_SHA from .env is ignored.
# Otherwise a temporary checkout of matter sdk will be made.

# Paths
ROOT_DIR=$(realpath $(dirname "$0")/..)
TEST_YAML_LOCK_PATH="$ROOT_DIR/.lock-test-yaml"
TMP_SDK_FOLDER="sdk-sparse"
TMP_SDK_PATH="/tmp/$TMP_SDK_FOLDER"

SDK_YAML_PATH="src/app/tests/suites/certification"
SDK_SCRIPTS_PATH="scripts/"
SDK_EXAMPLE_CHIP_TOOL_PATH="examples/chip-tool"
SDK_EXAMPLE_PLACEHOLDER_PATH="examples/placeholder"
SDK_DATA_MODEL_PATH="src/app/zap-templates/zcl/data-model/chip"

ENV_FILE="$ROOT_DIR/.env"

TEST_COLLECTIONS_PATH="$ROOT_DIR/test_collections"
YAML_TEST_COLLECTION_PATH="$TEST_COLLECTIONS_PATH/yaml_tests"
YAML_DIR_YAML_TEST_COLLECTION_PATH="$YAML_TEST_COLLECTION_PATH/yaml"
SDK_YAML_DIR_YAML_TEST_COLLECTION_PATH="$YAML_DIR_YAML_TEST_COLLECTION_PATH/sdk"
SDK_YAML_VERSION="$SDK_YAML_DIR_YAML_TEST_COLLECTION_PATH/.version"

install_matter_wheels () {
  pip install ${YAML_TEST_COLLECTION_PATH}/sdk_runner/*.whl
}

for arg in "$@"
do
    case $arg in
        --sdk-path=*) # usage --sdk-path=/user/home/ubuntu/matter-sdk
        SDK_PATH="${arg#*=}"
        shift # Remove ---sdk-path=<path> from processing
        ;;
        --force-update) # skip version check and force update
        FORCE_UPDATE=1
        shift # Remove --force-update from processing
        ;;
        *)
        OTHER_ARGUMENTS+=("$1")
        shift # Remove generic argument from processing
        ;;
    esac
done

if [[ -v SDK_PATH ]]
then
    echo "Using custom SDK path: ${SDK_PATH}. Update required"
    YAML_VERSION="custom-sdk"
else
    # Get configured SDK_SHA (will default to value in app/core/config.py)
    SDK_SHA=`LOGGING_LEVEL=critical python3 -c "from app.core.config import settings; print(settings.SDK_SHA)"`
    if [[ $FORCE_UPDATE -eq 1 ]]
    then 
        echo "Update is forced."
        YAML_VERSION=$SDK_SHA
    elif [ -f "$TEST_YAML_LOCK_PATH" ]
    then 
        echo "Test yaml are locked by '.lock-test-yaml', remove file to update."
        exit 0
    elif [ ! -f "$SDK_YAML_VERSION" ] || [[ $(< "$SDK_YAML_VERSION") != "$SDK_SHA" ]]
    then    echo "Current version of test yaml needs to be updated to SDK: $SDK_SHA"
        YAML_VERSION=$SDK_SHA
    else
        echo "Current version of test yaml are up to date with SDK: $SDK_SHA"
        # Need to install wheels after docker restart.
        install_matter_wheels
        exit 0
    fi
fi
# If SDK path is not present, then do local checkout
if [ -z "$SDK_PATH" ]
then
    # Checkout SDK sparsely 
    cd /tmp
    rm -rf $TMP_SDK_PATH
    git clone --filter=blob:none --no-checkout --depth 1 --sparse https://github.com/project-chip/connectedhomeip.git $TMP_SDK_FOLDER
    cd $TMP_SDK_FOLDER
    git sparse-checkout init
    git sparse-checkout set $SDK_YAML_PATH $SDK_SCRIPTS_PATH $SDK_EXAMPLE_PLACEHOLDER_PATH $SDK_EXAMPLE_CHIP_TOOL_PATH $SDK_DATA_MODEL_PATH
    git checkout -q $SDK_SHA
    git apply $ROOT_DIR/sdk_patch/TestHarnessSDKChanges.patch
    SDK_PATH="$TMP_SDK_PATH"
fi

if [ ! -d "$SDK_PATH" ] 
then
    echo "Unexpected: SDK path: $SDK_PATH DOES NOT exists." 
    exit 1
fi

# Clear old SDK YAMLs
if [ -d "$SDK_YAML_DIR_YAML_TEST_COLLECTION_PATH" ]; then rm -Rf $SDK_YAML_DIR_YAML_TEST_COLLECTION_PATH; fi
mkdir -p $SDK_YAML_DIR_YAML_TEST_COLLECTION_PATH

# Records SDK Version
echo "$YAML_VERSION" > "$SDK_YAML_VERSION"

# Copy SDK YAMLs and other (including default pics)
cd "$SDK_PATH/$SDK_YAML_PATH"
cp * "$SDK_YAML_DIR_YAML_TEST_COLLECTION_PATH/"

# Delete deprecated codegenerated python wrappers for yaml 
rm -Rf "$TEST_COLLECTIONS_PATH/manual_tests"
rm -Rf "$TEST_COLLECTIONS_PATH/automated_and_semi_automated"
rm -Rf "$TEST_COLLECTIONS_PATH/app1_tests"

###
# Extract sdk runner and dependencies
###
EXTRACTION_ROOT="$YAML_TEST_COLLECTION_PATH/sdk_runner"

# Remove existing extraction
rm -rf ${EXTRACTION_ROOT}

# Create python wheels in temp folder and copy to sdk_runner
# The main code for the runner is made of:
#   1. matter_idl.                This is a python implementation of an xml parser for the cluster definition.
#   2. matter_yamltests           This is a python implementation of a yaml parser.
#   3. matter_chip_tool_adapter   This is an adapter that translates the yaml result from the parser to chip-tool commands.
#                                 If needed it exists an adapter for the "examples/placeholder" applications and an
#                                 adapter for chip-repl.
#   4. wrapper code               The code that glues all of that together.

mkdir -p ${EXTRACTION_ROOT}

cd ${SDK_PATH}/scripts/py_matter_idl
python -m build --outdir ${EXTRACTION_ROOT}
cd ${SDK_PATH}/scripts/py_matter_yamltests
python -m build --outdir ${EXTRACTION_ROOT}
cd ${SDK_PATH}/examples/chip-tool/py_matter_chip_tool_adapter
python -m build --outdir ${EXTRACTION_ROOT}
cd ${SDK_PATH}/examples/placeholder/py_matter_placeholder_adapter
python -m build --outdir ${EXTRACTION_ROOT}
install_matter_wheels

# The runner needs some cluster definitions to used when parsing the YAML test. It allows to properly translate YAML
# commands. For example, it ensure that a string defined in YAML is converted to the right format between a CHAR_STRING or
# an OCTET_STRING.
# The default folder where cluster definitions can be found is src/app/zap-templates/zcl/data-model/chip.
mkdir -p ${EXTRACTION_ROOT}/specifications/
cp -r ${SDK_PATH}/src/app/zap-templates/zcl/data-model/chip ${EXTRACTION_ROOT}/specifications/

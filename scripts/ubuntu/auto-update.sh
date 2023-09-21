#! /usr/bin/env bash
ROOT_DIR=$(realpath $(dirname "$0")/../..)
SCRIPT_DIR="$ROOT_DIR/scripts"
UBUNTU_SCRIPT_DIR="$SCRIPT_DIR/ubuntu"

if [ $# != 1 ] || [ $1 = "--help" ]; then
  echo "Usage:"
  echo "./scripts/auto-update.sh <branch_name>"
  echo "Mandatory: <branch_name>  branch name"
  exit 1
fi

BRANCH_NAME=$1

# It is necessary to update the branch references from origin
# to prevent unrecognized branch error during checkout.
git fetch 

printf "\n\n**********"
printf "\n*** Getting Test Harness code ***\n"

$SCRIPT_DIR/update.sh "$BRANCH_NAME"

printf "\n\n**********"
printf "\n*** Fetching sample apps ***\n"
$UBUNTU_SCRIPT_DIR/update-sample-apps.sh

printf "\n\n**********"
printf "\n*** Fetching PAA Certs from SDK ***\n"
$UBUNTU_SCRIPT_DIR/update-paa-certs.sh

printf "\n\n**********"
printf "\n*** Stoping Containers ***\n"
$SCRIPT_DIR/stop.sh

printf "\n\n**********"
printf "\n*** Building Clean Images ***\n"
$SCRIPT_DIR/build-no-cache.sh

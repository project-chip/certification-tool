#! /usr/bin/env bash

 #
 # Copyright (c) 2026 Project CHIP Authors
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 # http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.

# Checks the currently checked-out branch against the Test Harness version
# policy published on the base repository's 'main' branch.
#
# Exit codes:
#   0 - OK to proceed (up to date, dev branch, or check skipped)
#   1 - This version must not be used (denylisted or below the minimum
#       supported version); caller should take the Test Harness down.

ROOT_DIR=$(realpath "$(dirname "$0")/../..")
REPO_URL="https://github.com/project-chip/certification-tool.git"
POLICY_PATH="scripts/version-check/version_policy.conf"
FETCH_TIMEOUT_SECS=10

source "$(dirname "$0")/version-lib.sh"

if ! command -v git >/dev/null 2>&1; then
    print_warning "WARNING: git is not installed; skipping Test Harness version check."
    exit 0
fi

if ! git -C "$ROOT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    print_warning "WARNING: '$ROOT_DIR' is not a git checkout (it may have been copied rather than cloned); skipping Test Harness version check."
    exit 0
fi

CURRENT_BRANCH=$(detect_current_branch "$ROOT_DIR")

POLICY_DATA=""
if timeout "$FETCH_TIMEOUT_SECS" git -C "$ROOT_DIR" fetch --quiet --depth=1 "$REPO_URL" main >/dev/null 2>&1; then
    POLICY_DATA=$(git -C "$ROOT_DIR" show FETCH_HEAD:"$POLICY_PATH" 2>/dev/null)
else
    print_warning "WARNING: could not reach '$REPO_URL' to check the Test Harness version policy (this can happen behind restrictive firewalls)."
fi

REMOTE_HEADS=$(timeout "$FETCH_TIMEOUT_SECS" git ls-remote --heads "$REPO_URL" 2>/dev/null)

evaluate_version_policy "$CURRENT_BRANCH" "$POLICY_DATA" "$REMOTE_HEADS"
exit $?

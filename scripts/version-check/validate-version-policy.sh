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

# Validates scripts/version-check/version_policy.conf's format: catches
# typos in keys and malformed version strings before they ship. At
# runtime, a malformed policy is only ever treated as "unreadable" and
# silently skipped (see evaluate_version_policy in version-lib.sh) --
# this is what actually catches a mistake, in CI, before it merges.

SCRIPT_DIR="$(dirname "$0")"
POLICY_FILE="${1:-$SCRIPT_DIR/version_policy.conf}"

source "$SCRIPT_DIR/version-lib.sh"

if [[ ! -f "$POLICY_FILE" ]]; then
    echo "ERROR: policy file '$POLICY_FILE' not found."
    exit 1
fi

ERRORS=0
MIN_VERSION_COUNT=0
LINE_NUM=0

while IFS= read -r line || [[ -n "$line" ]]; do
    LINE_NUM=$((LINE_NUM + 1))
    stripped="${line%%#*}"
    [[ -z "${stripped//[[:space:]]/}" ]] && continue

    if [[ "$stripped" != *=* ]]; then
        echo "ERROR: line $LINE_NUM: expected 'key=value', got: $line"
        ERRORS=$((ERRORS + 1))
        continue
    fi

    key="${stripped%%=*}"
    value="${stripped#*=}"

    case "$key" in
        minimum_version)
            MIN_VERSION_COUNT=$((MIN_VERSION_COUNT + 1))
            if ! matches_release_convention "$value"; then
                echo "ERROR: line $LINE_NUM: minimum_version value '$value' does not match the expected vMAJOR.MINOR[.PATCH]+season_year convention."
                ERRORS=$((ERRORS + 1))
            fi
            ;;
        denylisted_version)
            if ! matches_release_convention "$value"; then
                echo "ERROR: line $LINE_NUM: denylisted_version value '$value' does not match the expected vMAJOR.MINOR[.PATCH]+season_year convention."
                ERRORS=$((ERRORS + 1))
            fi
            ;;
        *)
            echo "ERROR: line $LINE_NUM: unrecognized key '$key' (expected 'minimum_version' or 'denylisted_version') -- possible typo?"
            ERRORS=$((ERRORS + 1))
            ;;
    esac
done < "$POLICY_FILE"

if [[ "$MIN_VERSION_COUNT" -eq 0 ]]; then
    echo "ERROR: no 'minimum_version' entry found."
    ERRORS=$((ERRORS + 1))
elif [[ "$MIN_VERSION_COUNT" -gt 1 ]]; then
    echo "ERROR: found $MIN_VERSION_COUNT 'minimum_version' entries; exactly one is allowed."
    ERRORS=$((ERRORS + 1))
fi

if [[ "$ERRORS" -gt 0 ]]; then
    echo
    echo "$POLICY_FILE failed validation with $ERRORS error(s)."
    exit 1
fi

echo "$POLICY_FILE is valid."

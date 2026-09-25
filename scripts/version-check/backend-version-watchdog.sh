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

# Runs periodically as the backend container's Docker healthcheck (see
# docker-compose.yml). Re-checks the version policy for long-running
# installs that were compliant at 'start.sh' time but have since been
# denylisted or fallen below the minimum supported version.
#
# Unlike scripts/check-th-version.sh (which runs on the host before
# anything is started), this runs *inside* the already-running backend
# container, so it must never interrupt a test run in progress: if the
# version is no longer allowed, it only stops the stack once it confirms
# no test run is currently executing. If it can't confirm that, it leaves
# everything running and tries again on the next scheduled check.
#
# Exit codes only affect the container's reported Docker health status
# (0 = healthy, 1 = unhealthy); the actual shutdown, when it happens, is
# performed directly by this script via the mounted docker socket.
#
# Docker runs this on docker-compose.yml's short healthcheck interval so
# the container reports healthy (and becomes Traefik-routable) soon after
# it starts, not once a day. The version-policy fetch (network calls) is
# expensive and only meant to happen about once a day, so it's throttled
# via a timestamp stamp file rather than Docker's interval. Once a fetch
# finds the version denylisted, that verdict is cached in a separate flag
# file so the (cheap, local) safe_to_stop check can still be polled every
# tick without re-hitting the network for as long as a test keeps running.

REPO_URL="https://github.com/project-chip/certification-tool.git"
RAW_POLICY_URL="https://raw.githubusercontent.com/project-chip/certification-tool/main/scripts/version-check/version_policy.conf"
FETCH_TIMEOUT_SECS=10
RECHECK_INTERVAL_SECS=$((24 * 60 * 60))
LAST_CHECK_STAMP="/tmp/.backend-version-watchdog-last-check"
DENYLISTED_FLAG="/tmp/.backend-version-watchdog-denylisted"

if ! source "$(dirname "$0")/version-lib.sh"; then
    printf '%s\n' "ERROR: could not load version-lib.sh." >&2
    exit 1
fi

CURRENT_BRANCH="${TH_CURRENT_BRANCH:-}"

if [[ -z "$CURRENT_BRANCH" ]]; then
    print_warning "WARNING: TH_CURRENT_BRANCH is not set; skipping Test Harness version check."
    exit 0
fi

# Skip straight to the (cheap) safe_to_stop poll if a prior fetch already
# found this version denylisted -- no need to re-hit the network every
# tick while we wait for the test run to finish.
if [[ ! -f "$DENYLISTED_FLAG" ]]; then
    if [[ -f "$LAST_CHECK_STAMP" ]]; then
        LAST_CHECK=$(<"$LAST_CHECK_STAMP")
        if [[ "$LAST_CHECK" =~ ^[0-9]+$ ]] && (( $(date +%s) - LAST_CHECK < RECHECK_INTERVAL_SECS )); then
            exit 0
        fi
    fi

    POLICY_DATA=$(curl -fsS --max-time "$FETCH_TIMEOUT_SECS" "$RAW_POLICY_URL" 2>/dev/null)
    REMOTE_HEADS=$(timeout "$FETCH_TIMEOUT_SECS" git ls-remote --heads "$REPO_URL" 2>/dev/null)
    date +%s > "$LAST_CHECK_STAMP"

    if evaluate_version_policy "$CURRENT_BRANCH" "$POLICY_DATA" "$REMOTE_HEADS"; then
        exit 0
    fi

    : > "$DENYLISTED_FLAG"
fi

# Returns 0 only if we can positively confirm the test engine is idle (not
# loading, ready to run, or actively running a test). Any failure to check
# is treated as "not safe to stop".
safe_to_stop() {
    local status
    if ! status=$(curl -fsS --max-time "$FETCH_TIMEOUT_SECS" "http://localhost/api/v1/test_run_executions/status" 2>/dev/null); then
        print_warning "WARNING: could not query the Test Harness API to check the test runner status; leaving the Test Harness running."
        return 1
    fi
    [[ "$status" == *'"idle"'* ]]
}

if ! safe_to_stop; then
    print_warning "The test engine is not idle (a test is loading, ready, or running); deferring shutdown. Will check again on the next scheduled interval."
    exit 1
fi

print_error "The test engine is idle. Taking down the Test Harness."
PROJECT=$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project" }}' "$HOSTNAME" 2>/dev/null)
if [[ -z "$PROJECT" ]]; then
    print_error "ERROR: could not determine the docker compose project; unable to stop the Test Harness automatically."
    exit 1
fi
OTHER_IDS=$(docker ps -q --filter "label=com.docker.compose.project=$PROJECT" | grep -v "^$(docker inspect --format '{{.Id}}' "$HOSTNAME" | cut -c1-12)")
[[ -n "$OTHER_IDS" ]] && docker stop $OTHER_IDS
docker stop "$HOSTNAME"

exit 1

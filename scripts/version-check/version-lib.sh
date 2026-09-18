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

# Shared helpers for parsing/comparing Test Harness release branch names
# (vMAJOR.MINOR[.PATCH][-beta N[.N] | -rc N]+season_year). Sourced by both
# scripts/check-th-version.sh (host) and scripts/backend-version-watchdog.sh
# (runs inside the backend container).

BRANCH_REGEX='^v[0-9]+\.[0-9]+(\.[0-9]+)?(-(beta|rc)[0-9]+(\.[0-9]+)?)?\+[a-z]+[0-9]{4}$'

# Color is only used for these two message classes, so severity is visible
# at a glance: yellow for a warning where execution/startup still
# continues, red for an error that means the Test Harness is being shut
# down. Disabled automatically when stdout isn't a terminal (e.g. Docker
# healthcheck output), so logs don't fill up with raw escape codes.
if [[ -t 1 ]]; then
    COLOR_YELLOW=$'\033[33m'
    COLOR_RED=$'\033[31m'
    COLOR_RESET=$'\033[0m'
else
    COLOR_YELLOW=""
    COLOR_RED=""
    COLOR_RESET=""
fi

print_warning() {
    printf '%s%s%s\n' "$COLOR_YELLOW" "$*" "$COLOR_RESET"
}

print_error() {
    printf '%s%s%s\n' "$COLOR_RED" "$*" "$COLOR_RESET"
}

matches_release_convention() {
    [[ "$1" =~ $BRANCH_REGEX ]]
}

is_beta_branch() {
    [[ "$1" == *-beta* || "$1" == *-rc* ]]
}

# Prints a zero-padded, lexically-sortable "MMMMMmmmmmppppp" key for a
# vMAJOR.MINOR[.PATCH]... branch/version string, or prints nothing and
# returns 1 if it doesn't start with a version number.
version_sort_key() {
    if [[ ! "$1" =~ ^v([0-9]+)\.([0-9]+)(\.([0-9]+))? ]]; then
        return 1
    fi
    printf '%05d%05d%05d' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}" "${BASH_REMATCH[4]:-0}"
}

# Resolves the version identifier for the given checkout: the current
# branch name, or -- if HEAD is detached because a release was checked
# out as a tag rather than a branch -- the exact tag name at HEAD.
detect_current_branch() {
    local root_dir="$1" ref
    ref=$(git -C "$root_dir" rev-parse --abbrev-ref HEAD 2>/dev/null) || ref=""
    if [[ "$ref" == "HEAD" ]]; then
        ref=$(git -C "$root_dir" describe --tags --exact-match 2>/dev/null) || ref="HEAD"
    fi
    printf '%s' "$ref"
}

print_upgrade_instructions() {
    echo "  To upgrade the Test Harness, run:"
    echo "    ./scripts/update-th-code.sh $1"
    echo "    ./scripts/update.sh"
}

# Reads `git ls-remote --heads` output from stdin and prints the highest
# non-beta release branch name matching the naming convention (empty if
# none match).
find_latest_release_branch() {
    local latest_branch="" latest_key="" line candidate candidate_key
    while IFS= read -r line; do
        candidate="${line#*refs/heads/}"
        [[ -z "$candidate" || "$candidate" == "$line" ]] && continue
        is_beta_branch "$candidate" && continue
        matches_release_convention "$candidate" || continue
        candidate_key=$(version_sort_key "$candidate") || continue
        if [[ -z "$latest_key" || "$candidate_key" > "$latest_key" ]]; then
            latest_key="$candidate_key"
            latest_branch="$candidate"
        fi
    done
    printf '%s' "$latest_branch"
}

# Given the current branch name, the version_policy.json contents, and
# `git ls-remote --heads` output for the base repository, prints all
# warnings/notices/errors and decides whether this version may run.
# Fetching those three inputs is left to the caller, since it differs
# between a host git checkout (scripts/check-th-version.sh) and the
# backend container (scripts/backend-version-watchdog.sh).
#
# Returns:
#   0 - OK to proceed (dev branch, unparseable branch, up to date, or
#       above the minimum and not denylisted)
#   1 - This version must not be used (denylisted or below the minimum
#       supported version)
evaluate_version_policy() {
    local current_branch="$1" policy_data="$2" remote_heads="$3"

    if ! matches_release_convention "$current_branch"; then
        print_warning "WARNING: current branch '$current_branch' does not match the expected Test Harness release naming convention (vMAJOR.MINOR[.PATCH]+season_year)."
        print_warning "         Assuming this is a development branch; skipping version enforcement."
        return 0
    fi

    if is_beta_branch "$current_branch"; then
        print_warning "WARNING: '$current_branch' is a beta branch. All certification testing must be run from an official release branch, not a beta."
    fi

    if [[ -z "$policy_data" ]]; then
        print_warning "WARNING: could not read the Test Harness version policy. Skipping version enforcement."
        return 0
    fi

    # Parsed as plain "key=value" data (never sourced/eval'd) -- see
    # scripts/version_policy.conf for the format.
    local min_version="" denylisted=false line key value
    while IFS= read -r line; do
        line="${line%%#*}"
        [[ -z "${line//[[:space:]]/}" ]] && continue
        key="${line%%=*}"
        value="${line#*=}"
        case "$key" in
            minimum_version) min_version="$value" ;;
            denylisted_version) [[ "$value" == "$current_branch" ]] && denylisted=true ;;
        esac
    done <<< "$policy_data"

    if [[ -z "$min_version" ]]; then
        print_warning "WARNING: version policy is malformed or unreadable. Skipping version enforcement."
        return 0
    fi

    local current_key min_key
    current_key=$(version_sort_key "$current_branch")
    min_key=$(version_sort_key "$min_version")

    local below_minimum=false
    if [[ -n "$current_key" && -n "$min_key" && "$current_key" < "$min_key" ]]; then
        below_minimum=true
    fi

    local latest_branch latest_key=""
    latest_branch=$(printf '%s' "$remote_heads" | find_latest_release_branch)
    [[ -n "$latest_branch" ]] && latest_key=$(version_sort_key "$latest_branch")

    # A beta's sort key equals the sort key of the eventual GA release for
    # the same major.minor.patch line (beta-ness isn't part of the key),
    # so a beta must also notify on an *equal* key -- that's the case
    # where the release matching this exact beta has now shipped as GA --
    # not just a strictly greater one.
    local new_version_available=false
    if [[ -n "$latest_key" && -n "$current_key" ]]; then
        if [[ "$current_key" < "$latest_key" ]]; then
            new_version_available=true
        elif [[ "$current_key" == "$latest_key" ]] && is_beta_branch "$current_branch"; then
            new_version_available=true
        fi
    fi

    if [[ "$denylisted" != true && "$below_minimum" != true ]]; then
        if [[ "$new_version_available" == true ]]; then
            if [[ "$current_key" == "$latest_key" ]]; then
                echo "NOTICE: an official release for this beta is now available: '$latest_branch' (you are on '$current_branch')."
            else
                echo "NOTICE: a newer Test Harness version is available: '$latest_branch' (you are on '$current_branch')."
            fi
            print_upgrade_instructions "$latest_branch"
        fi
        return 0
    fi

    print_error "################################################################################"
    if [[ "$denylisted" == true ]]; then
        print_error "ERROR: branch '$current_branch' has been disabled and must not be used for certification testing."
    else
        print_error "ERROR: branch '$current_branch' is older than the minimum supported version ($min_version)."
    fi
    print_error "################################################################################"
    [[ -n "$latest_branch" ]] && print_upgrade_instructions "$latest_branch"
    return 1
}

#!/usr/bin/env bash
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
#
# Prepare the Test Harness (TH) and run TC-CNET-4.12 with th-cli.
# Run ON THE TH (use `ssh -t` so that sudo and the th-cli prompts work).
# See docs/development/Running_TC-CNET-4.12_on_the_TH for what this does and why.
#
# HELP_BEGIN
# Required environment:
#   DUT_DISCRIMINATOR     DUT discriminator (decimal), e.g. 3840
#   DUT_SETUP_CODE        DUT setup passcode, e.g. 20202021
#   THREAD1_DATASET_HEX   operational dataset (hex) of the FIRST Thread network, the one
#                         served by the EXTERNAL border router; the DUT is commissioned there
# Optional environment:
#   THREAD2_DATASET_HEX   dataset (hex) to load on the TH's own OTBR as the SECOND network.
#                         If unset, a new random dataset is generated on every run.
#   THREAD2_CHANNEL       channel for a generated dataset (default 25, or 20 if THREAD1 uses 25)
#   OTBR_ON_MESH_PREFIX   on-mesh prefix for the TH OTBR (default fd11:<extpanid[0:4]>::/64)
#   INFRA_IFACE           TH uplink interface (default: interface of the default route)
#   OTBR_CONTAINER        OTBR container name (default otbr-chip)
#   CONFIG_FILE           config to write (default ~/cnet412_config.json)
#   QR_CODE               optional MT:... code, added as test parameter qr-code
#
# Options:
#   --start-otbr   (re)start the OTBR container with otbr_start.sh first (needs sudo)
#   --prepare-only prepare OTBR and write the config, do not run the test
#   --dry-run      print what would be done, change nothing
# HELP_END
set -euo pipefail

OTBR_CONTAINER="${OTBR_CONTAINER:-otbr-chip}"
CONFIG_FILE="${CONFIG_FILE:-$HOME/cnet412_config.json}"
CERT_TOOL_DIR="${CERT_TOOL_DIR:-$HOME/certification-tool}"
OTBR_START="$CERT_TOOL_DIR/backend/test_collections/matter/scripts/OTBR/otbr_start.sh"
export PATH="$HOME/.local/bin:$PATH"

START_OTBR=0
PREPARE_ONLY=0
DRY_RUN=0
for arg in "$@"; do
    case "$arg" in
        --start-otbr) START_OTBR=1 ;;
        --prepare-only) PREPARE_ONLY=1 ;;
        --dry-run) DRY_RUN=1 ;;
        -h | --help) sed -n '/^# HELP_BEGIN$/,/^# HELP_END$/p' "$0" | sed '1d;$d'; exit 0 ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }

: "${DUT_DISCRIMINATOR:?set DUT_DISCRIMINATOR}"
: "${DUT_SETUP_CODE:?set DUT_SETUP_CODE}"
: "${THREAD1_DATASET_HEX:?set THREAD1_DATASET_HEX}"

# Decimal passcode / discriminator only: they end up in a JSON file.
[[ "$DUT_DISCRIMINATOR" =~ ^[0-9]+$ ]] || die "DUT_DISCRIMINATOR must be decimal"
[[ "$DUT_SETUP_CODE" =~ ^[0-9]+$ ]] || die "DUT_SETUP_CODE must be decimal"
[[ "$THREAD1_DATASET_HEX" =~ ^[0-9a-fA-F]+$ ]] || die "THREAD1_DATASET_HEX must be hex"
if [[ -n "${THREAD2_DATASET_HEX:-}" ]]; then
    [[ "$THREAD2_DATASET_HEX" =~ ^[0-9a-fA-F]+$ ]] || die "THREAD2_DATASET_HEX must be hex"
fi

run() {
    if [[ $DRY_RUN -eq 1 ]]; then echo "[dry-run] $*"; else "$@"; fi
}

# Docker without sudo if the user is in the docker group, otherwise with sudo.
DOCKER=(docker)
if ! docker ps > /dev/null 2>&1; then DOCKER=(sudo docker); fi

ot() { "${DOCKER[@]}" exec "$OTBR_CONTAINER" ot-ctl "$@"; }
ot_out() { ot "$@" | tr -d '\r' | grep -v '^Done$'; }

# Print "<channel> <extpanid>" of a dataset in hex (Thread TLV format).
dataset_field() {
    python3 - "$1" "$2" << 'PY'
import sys
data = bytes.fromhex(sys.argv[1])
want = sys.argv[2]
i = 0
fields = {}
while i + 2 <= len(data):
    t, l = data[i], data[i + 1]
    v = data[i + 2:i + 2 + l]
    if t == 0 and l == 3:
        fields["channel"] = str(int.from_bytes(v[1:3], "big"))
    elif t == 2 and l == 8:
        fields["extpanid"] = v.hex()
    i += 2 + l
print(fields.get(want, ""))
PY
}

# ---------------------------------------------------------------- preflight
info "Preflight"
command -v th-cli > /dev/null || die "th-cli not found in PATH"
command -v python3 > /dev/null || die "python3 not found"
INFRA_IFACE="${INFRA_IFACE:-$(ip route show default | awk '/default/ {print $5; exit}')}"
[[ -n "$INFRA_IFACE" ]] || die "cannot detect INFRA_IFACE, set it"
echo "infra interface: $INFRA_IFACE"

STATUS="$(th-cli test-runner-status 2>&1 || true)"
echo "$STATUS" | grep -q "IDLE" || die "test runner is not IDLE: $STATUS"

T1_CHANNEL="$(dataset_field "$THREAD1_DATASET_HEX" channel)"
T1_EXTPAN="$(dataset_field "$THREAD1_DATASET_HEX" extpanid)"
[[ -n "$T1_CHANNEL" && -n "$T1_EXTPAN" ]] || die "THREAD1_DATASET_HEX has no channel/extpanid TLV"
echo "network 1: channel $T1_CHANNEL, extpanid $T1_EXTPAN"

# ---------------------------------------------------------------- OTBR container
if [[ $START_OTBR -eq 1 ]]; then
    info "Starting OTBR container with otbr_start.sh (sudo)"
    [[ -x "$OTBR_START" ]] || die "$OTBR_START not found"
    run "$OTBR_START" -i "$INFRA_IFACE"
fi

if [[ $DRY_RUN -eq 0 ]]; then
    "${DOCKER[@]}" ps --format '{{.Names}}' | grep -qx "$OTBR_CONTAINER" \
        || die "container $OTBR_CONTAINER is not running; rerun with --start-otbr"
    ot state > /dev/null || die "ot-ctl does not answer in $OTBR_CONTAINER"
    if ! "${DOCKER[@]}" exec "$OTBR_CONTAINER" test -f /etc/avahi/avahi-daemon.conf; then
        echo "WARNING: /etc/avahi/avahi-daemon.conf is missing inside $OTBR_CONTAINER." >&2
        echo "         otbr_start.sh may mount a stale avahi path (see the guide, 'Known issues')." >&2
    fi
fi

# ---------------------------------------------------------------- dataset for network 2
if [[ -n "${THREAD2_DATASET_HEX:-}" ]]; then
    T2_HEX="$THREAD2_DATASET_HEX"
    T2_MODE=set
else
    T2_MODE=generate
    if [[ -n "${THREAD2_CHANNEL:-}" ]]; then
        T2_CHANNEL="$THREAD2_CHANNEL"
    elif [[ "$T1_CHANNEL" == "25" ]]; then
        T2_CHANNEL=20
    else
        T2_CHANNEL=25
    fi
    [[ "$T2_CHANNEL" != "$T1_CHANNEL" ]] || die "network 2 must not use the channel of network 1 ($T1_CHANNEL)"
fi

info "Configuring Thread network 2 on $OTBR_CONTAINER (mode: $T2_MODE)"
run ot thread stop
run ot ifconfig down
if [[ "$T2_MODE" == set ]]; then
    run ot dataset set active "$T2_HEX"
else
    run ot dataset init new
    run ot dataset channel "$T2_CHANNEL"
    run ot dataset commit active
fi
run ot ifconfig up
run ot thread start

if [[ $DRY_RUN -eq 0 ]]; then
    for _ in $(seq 1 60); do
        [[ "$(ot_out state)" == "leader" ]] && break
        sleep 1
    done
    STATE="$(ot_out state)"
    if [[ "$STATE" != "leader" ]]; then
        # "child"/"router" means another node already holds a partition with the same
        # network key/extpanid, usually a DUT left over from a previous run.
        die "OTBR state is '$STATE', expected 'leader' (reset the DUT, check for another OTBR with the same dataset)"
    fi
    T2_HEX="$(ot_out dataset active -x)"
    [[ -z "${THREAD2_DATASET_HEX:-}" ]] || [[ "${T2_HEX,,}" == "${THREAD2_DATASET_HEX,,}" ]] \
        || die "active dataset differs from THREAD2_DATASET_HEX"
else
    T2_HEX="${T2_HEX:-<generated dataset>}"
fi

T2_EXTPAN="$(dataset_field "$T2_HEX" extpanid 2> /dev/null || true)"
if [[ -z "${OTBR_ON_MESH_PREFIX:-}" ]]; then
    [[ -n "$T2_EXTPAN" ]] || T2_EXTPAN="0000"
    OTBR_ON_MESH_PREFIX="fd11:${T2_EXTPAN:0:4}::/64"
fi
[[ "$T2_EXTPAN" != "$T1_EXTPAN" || $DRY_RUN -eq 1 ]] || die "network 1 and network 2 have the same extpanid"

# The on-mesh prefix lets the TH route to the DUT through the OTBR; netdata register and the
# SRP server make the DUT's _matter._tcp record discoverable (without 'srp server enable' the
# DUT never registers, see certification-tool-backend PR #342).
run ot prefix add "$OTBR_ON_MESH_PREFIX" pasor
run ot netdata register
run ot srp server enable

if [[ $DRY_RUN -eq 0 ]]; then
    [[ "$(ot_out srp server state)" == "running" ]] || die "SRP server is not running on $OTBR_CONTAINER"
    ot_out netdata show | grep -Eq '^[0-9]+ 5d ' || die "no DNS/SRP service (0x5d) in the Thread network data"
    echo "network 2: channel $(dataset_field "$T2_HEX" channel), extpanid $T2_EXTPAN, prefix $OTBR_ON_MESH_PREFIX"
fi

# ---------------------------------------------------------------- config
info "Writing $CONFIG_FILE"
if [[ $DRY_RUN -eq 0 ]]; then
    umask 077
    T1="$THREAD1_DATASET_HEX" T2="$T2_HEX" python3 - "$CONFIG_FILE" << 'PY'
import json, os, sys

cfg = {
    # rcp_serial_path=null keeps th-cli's default thread block (merged in by the CLI) from being
    # parsed as ThreadAutoConfig, which would make the backend start its own OTBR.
    "network": {"thread": {"operational_dataset_hex": os.environ["T1"], "rcp_serial_path": None}},
    "dut_config": {
        "pairing_mode": "ble-thread",
        "discriminator": os.environ["DUT_DISCRIMINATOR"],
        "setup_code": os.environ["DUT_SETUP_CODE"],
    },
    "test_parameters": {
        "string-arg": "PIXIT.CNET.THREAD_2ND_OPERATIONALDATASET:" + os.environ["T2"],
        "endpoint": 0,
    },
}
if os.environ.get("QR_CODE"):
    cfg["test_parameters"]["qr-code"] = os.environ["QR_CODE"]
with open(sys.argv[1], "w") as f:
    json.dump(cfg, f, indent=2)
PY
fi

[[ $PREPARE_ONLY -eq 0 ]] || { info "Prepared. Run: th-cli run-tests --tests-list TC_CNET_4_12 --config $CONFIG_FILE"; exit 0; }

# ---------------------------------------------------------------- run
cat << 'MSG'

Before continuing:
  - the DUT is factory reset, NOT commissioned, and in commissioning mode (BLE advertising
    is time limited on many devices: reset it right before answering the prompts below);
th-cli will ask two questions, read them before answering:
  "Do you want to reuse the previous commissioning information?"  -> 2 (NO)
  "Make sure the DUT is in Commissioning Mode"                    -> 1 (DONE)
MSG
if [[ $DRY_RUN -eq 1 ]]; then
    echo "[dry-run] th-cli run-tests --tests-list TC_CNET_4_12 --config $CONFIG_FILE --title \"TC-CNET-4.12 run\""
    exit 0
fi
read -r -p "Press Enter to start the test (Ctrl-C to abort)... " _
exec th-cli run-tests --tests-list TC_CNET_4_12 --config "$CONFIG_FILE" --title "TC-CNET-4.12 run"

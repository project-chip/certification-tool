# Running the Test Harness on WSL2 (development/test)

The Test Harness officially targets Raspberry Pi 4/5 and Ubuntu machines. It can
also run on WSL2 for development and test purposes, with the caveats below.

## Prerequisites

- WSL2 with systemd enabled (`/etc/wsl.conf` containing `[boot]` `systemd=true`)
- Ubuntu 24.04 with the username `ubuntu`

## Install

### 1. Run the standard installer

```bash
./scripts/ubuntu/auto-install.sh
```

The installer detects WSL. After detection, the following WSL specific behaviors
occur:

- Steps that do not apply are skipped:
  - The wpa_supplicant setup.
  - The wlan sysctl entries.
- The backend and frontend images are built locally from the submodules instead
  of downloading the arm64-only prebuilt ones (slower, no other impact).
- The sample apps installation is skipped with a notice: it requires the SDK
  image (`connectedhomeip/chip-cert-bins`), also arm64 only.
- Building the SDK image locally is an hour-long compile and is deliberately
  left as an explicit later step.
- The installer finishes with a reminder to build the image and run the update,
  which the next steps cover.
- The final reboot is replaced by logging out and back in:
  - Close the WSL terminal and open a new one, or restart WSL.
  - Docker group membership is applied on login.

### 2. Build the SDK image locally

Once logged back in, run the `build-local-sdk-image.sh` script, which compiles
the Matter SDK into a local image tagged exactly as the backend expects.

The tag is read from `backend/test_collections/matter/config.py`. The build
takes on the order of an hour:

```bash
./backend/test_collections/matter/scripts/build-local-sdk-image.sh
```

### 3. Install the sample apps

With the SDK image present locally, run the `update.sh` script to perform the
sample apps installation that was skipped during the install:

```bash
./scripts/update.sh
```

## Start the Test Harness

Run the `start.sh` script, which brings up the Test Harness containers. The backend
takes a few minutes to become ready, longer on the first start.

Then open http://localhost/ in the Windows browser (WSL2 forwards localhost by default):

```bash
./scripts/start.sh
```

## Limitations

- Reaching physical DUTs on the LAN depends on the WSL network mode: the default
  NAT network does not forward mDNS. Sample apps running inside the same WSL
  instance work without extra configuration.
- BLE and Thread (OTBR with a physical RCP) are untested on WSL.

## Troubleshooting

### The SDK image build fails at the pinned tag

The SDK Dockerfile fetches unpinned external tools, so the pinned tag can stop
building over time (e.g. at the current tag it builds gn from tip-of-tree
source, which no longer compiles). Retry with the current SDK Dockerfile, which
still builds the SDK at the pinned tag:

```bash
./backend/test_collections/matter/scripts/build-local-sdk-image.sh master
```

### The Test Harness is not up after starting WSL

The install enables the `matter-th` systemd service, which brings the Test
Harness up automatically when WSL starts. If the UI is unreachable, check the
service and start the Test Harness manually:

```bash
systemctl status matter-th
./scripts/start.sh
```

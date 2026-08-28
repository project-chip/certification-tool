# Running the Test Harness UI/CLI on WSL2 (development/test)

The Test Harness officially targets Raspberry Pi 4/5 and Ubuntu machines. It
can also run on WSL2 for development and test purposes, with the caveats
below.

This covers both the Test Harness UI and the CLI (`th-cli`): both are
installed by the setup and talk to the same local backend.

Everything WSL specific lives in this folder as an optional, self-contained
procedure: the standard install and update scripts are not modified. The
scripts here replay the stock install/update sequence, calling the stock
scripts unmodified wherever they work on WSL and substituting only the steps
that cannot work:

- The machine configuration runs without the wpa_supplicant setup and the
  wlan sysctl entries (WSL has no wlan interface).
- The backend, frontend, and SDK docker images are built locally (the
  published images are arm64 only).
- The final reboot is replaced by logging out and back in.

## Prerequisites

- WSL2 with systemd enabled (`/etc/wsl.conf` containing `[boot]`
  `systemd=true`)
- Ubuntu 24.04 with the username `ubuntu`

## Install

### 1. Run the WSL installer

```bash
./scripts/wsl/auto-install.sh
```

Notes on the run:

- The backend and frontend images build from the submodules during the
  install (slower than the download, no other impact).
- The SDK image (`connectedhomeip/chip-cert-bins`) and the test collections
  setup that depends on it (CLI, sample apps) are deferred to the two explicit
  steps below: the SDK image build is an hour-long compile, deliberately kept
  out of the installer.
- The installer ends with a logout note instead of a reboot: close the WSL
  terminal and open a new one, or restart WSL. Docker group membership is
  applied on login.

### 2. Build the SDK image locally

Once logged back in, run the `build-local-sdk-image.sh` script, which compiles
the Matter SDK into a local image tagged exactly as the backend expects. The
tag is automatically read from `backend/test_collections/matter/config.py`.

The build takes on the order of an hour:

```bash
./scripts/wsl/build-local-sdk-image.sh
```

### 3. Finish the setup

With the SDK image present locally, run the WSL update script to perform the
test collections setup that was deferred during the install (CLI installation
and sample apps copied to the ~/apps folder):

```bash
./scripts/wsl/update.sh
```

## Start the Test Harness

Run the `start.sh` script, which brings up the Test Harness containers. The
backend takes a few minutes to become ready, longer on the first start.

Then open http://localhost/ in the browser (WSL2 forwards localhost by
default):

```bash
./scripts/start.sh
```

## Updating

On WSL always use `./scripts/wsl/update.sh` instead of the stock
`./scripts/update.sh`: the stock script pulls the published arm64 images,
and on another architecture such a pull can still "succeed" with a platform
mismatch warning, silently overwriting the locally built images and breaking
the containers.

## Maintenance

The scripts here mirror parts of the stock install/update flow, synced
against the stock file versions recorded in `wsl-utils.sh`. When a mirrored
stock file changes, the WSL scripts print a warning at startup: review the
stock change, apply it to the WSL variant if it applies, and update the
recorded commit.

## Limitations

- Reaching physical DUTs on the LAN depends on the WSL network mode: the
  default NAT network does not forward mDNS. Sample apps running inside the
  same WSL instance work without extra configuration.
- BLE and Thread (OTBR with a physical RCP) are untested on WSL.

## Troubleshooting

### The SDK image build fails at the pinned tag

The SDK Dockerfile fetches unpinned external tools, so the pinned tag can stop
building over time. The build script automatically patches the known case (gn
built from tip-of-tree source, which no longer compiles). For other failures
in the tooling stages, retrying with the current SDK Dockerfile may help, but
its later stages may not match the pinned SDK commit:

```bash
./scripts/wsl/build-local-sdk-image.sh master
```

If both fail, the build logs (paths printed on failure) identify the failing
stage in each variant. From there: patch the pinned tag's Dockerfile for the
new issue (on failure the script prints the exact fetch, rebuild, and continue
commands for this), report it to the SDK, or wait for the Test Harness to move
to a newer SDK tag.

### The Test Harness is not up after starting WSL

The install enables the `matter-th` systemd service, which brings the Test
Harness up automatically when WSL starts. If the UI is unreachable, check the
service and start the Test Harness manually:

```bash
systemctl status matter-th
./scripts/start.sh
```

### Compose cannot find a locally built backend or frontend image

The image build scripts tag images with the current commit of the respective
submodule, while `docker-compose.yml` references a pinned tag. The two match on
a regular checkout of `main`. If the submodule is checked out elsewhere (e.g. a
development branch), the built tag differs from the pinned one and starting the
Test Harness tries to download the image instead. Retag the built image to the
pinned tag, for example for the backend:

```bash
# built tag: see `docker images` (it is the submodule's short commit hash)
# pinned tag: see the backend `image:` line in docker-compose.yml
docker tag ghcr.io/project-chip/csa-certification-tool-backend:<built_tag> \
           ghcr.io/project-chip/csa-certification-tool-backend:<pinned_tag>
```

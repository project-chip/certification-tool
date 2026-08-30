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
- The final reboot is dropped: the setup finishes and starts the Test Harness
  in one run.

## Prerequisites

- WSL2 with systemd enabled (`/etc/wsl.conf` containing `[boot]`
  `systemd=true`)
- Ubuntu 24.04 with the username `ubuntu`

## Install

The whole setup is a single unattended command, ending with the Test Harness
up and reachable at http://localhost/ (WSL2 forwards localhost by default):

```bash
./scripts/wsl/auto-install.sh
```

Notes on the run:

- The run takes on the order of 1.5 hours, dominated by the SDK image
  (`connectedhomeip/chip-cert-bins`) compile.
- The backend and frontend images build from the submodules (slower than the
  download, no other impact). Known build issues in the pinned submodules are
  patched automatically at build time, with a notice (currently one: an npm
  pin in backends that predate the nodejs/npm removal of
  [certification-tool-backend#341](https://github.com/project-chip/certification-tool-backend/pull/341)).
- No reboot or relogin: the install runs start to finish in one shell.
- If the run stops at the SDK image build (see Troubleshooting), finish the
  remaining steps manually once it builds: `./scripts/wsl/update.sh`, then
  start the Test Harness as below.

## Starting the Test Harness

The install leaves the Test Harness running, and the `matter-th` service
starts it when WSL starts. To start it manually, run the `start.sh` script;
the backend takes a few minutes to become ready, longer on the first start:

```bash
./scripts/start.sh
```

One caveat right after an install: shells and services started before it
(including the shell the installer ran in, and the VS Code WSL server) lack
the docker group membership it added, so docker commands there fail on
permissions until they are restarted. `newgrp docker` grants it to such a
shell in place; `wsl --shutdown` resets everything at once.

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
submodule, while `docker-compose.yml` references a pinned tag.
`build-local-images.sh` retags the built image to the pinned tag automatically
when they differ, so this only applies to images built by calling the
submodule build scripts directly. Retag the built image to the pinned tag,
for example for the backend:

```bash
# built tag: see `docker images` (it is the submodule's short commit hash)
# pinned tag: see the backend `image:` line in docker-compose.yml
docker tag ghcr.io/project-chip/csa-certification-tool-backend:<built_tag> \
           ghcr.io/project-chip/csa-certification-tool-backend:<pinned_tag>
```

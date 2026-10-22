# Running TC-CNET-4.12 on the TH

TC-CNET-4.12 checks the DUT's `ConnectNetwork` handling on Thread with **two
operational datasets**. The test moves the DUT between two Thread networks and
checks that the TH finds it again after every switch. It needs no OTA image.

`scripts/utils/run_cnet_4_12.sh` prepares the second network and runs the test.
It runs **on the TH**.

## How the test is laid out

```
              LAN (the TH's Wi-Fi/Ethernet)
      ┌─────────────────┼───────────────────────┐
 external border     TH (th-cli)        otbr-chip on the TH
 router (BR 1)                          (RCP dongle, BR 2)
      │                                          │
 Thread network 1                         Thread network 2
 (dataset 1)                              (dataset 2)
      └──────────── DUT (BLE + Thread) ──────────┘
```

| Step | What happens                                                                              |
| ---- | ----------------------------------------------------------------------------------------- |
| Pre  | TH commissions the DUT over BLE and gives it **dataset 1** (`operational_dataset_hex`).   |
| 5-9  | DUT is switched to **dataset 2** (`PIXIT.CNET.THREAD_2ND_OPERATIONALDATASET`).            |
| 10+  | DUT is switched back to dataset 1, then to dataset 2 and back once more.                  |

After each switch the TH waits for the DUT's `_matter._tcp` record, so:

-   The TH must reach **network 1** through an **external** border router on
    the same LAN as the TH. The router must advertise an IPv6 route to the
    Thread prefix into the LAN. Without it commissioning passes (BLE + PASE) and
    then fails with `CASESession ... Timeout`.
-   The TH must reach **network 2** through its own OTBR container (`otbr-chip`)
    with an RCP dongle. Its SRP server must be enabled, otherwise the DUT never
    registers.
-   Dataset 2 must be the dataset that is **active on the TH's OTBR**, and must
    differ from dataset 1 (channel, extended PAN ID, network key).

## Prerequisites

| Item                                                                                            | Check                                                         |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| TH on the same LAN as the external border router (Wi-Fi or Ethernet), IPv6 enabled              | `ip -6 route` shows a Thread prefix route learned from an RA  |
| Thread RCP dongle on the TH                                                                     | `ls -l /dev/ttyACM0`                                          |
| `th-cli` installed and the TH backend `healthy`                                                 | `th-cli available-tests \| grep TC_CNET_4_12`                 |
| `sudo` on the TH (only `otbr_start.sh` needs it)                                                | interactive `ssh -t` session                                  |
| Dataset 1 (hex) of the external network                                                         | on the border router: `ot-ctl dataset active -x`              |
| DUT: BLE, Thread, `NetworkCommissioning` with the Thread feature on endpoint 0, **factory reset** | DUT console / indicator                                       |

Datasets contain the network key. Do not put datasets of real networks into
documents or git.

### Moving the TH to the border router's network

If the TH is on Wi-Fi, configure the border router's SSID in netplan
(`/etc/netplan/*.yaml`, `wifis: wlan0: access-points:`). Keep an Ethernet
connection to your workstation, make a backup, and use
`sudo netplan try --timeout 120` so that a wrong setting rolls back. The TH's IP
changes, so refresh the SSH host key entry and prefer the IP over
`ubuntu.local`.

## Run

Use an interactive session: the script needs `sudo` for the OTBR container and
`th-cli` asks questions.

```bash
ssh -t ubuntu@<TH-IP>
export DUT_DISCRIMINATOR=3840 DUT_SETUP_CODE=20202021
export THREAD1_DATASET_HEX=<dataset 1 hex>
scripts/utils/run_cnet_4_12.sh --start-otbr --prepare-only   # prepare, check, stop
scripts/utils/run_cnet_4_12.sh --start-otbr                  # prepare and run
```

Drop `--start-otbr` when `otbr-chip` is already running. `--dry-run` prints what
would be done and changes nothing.

On the Wi-Fi-only TH the uplink is `wlan0`: the script takes it from the
default route (override with `INFRA_IFACE`).

The script:

1.  checks that the test runner is idle and reads the channel and extended PAN
    ID of dataset 1;
2.  (with `--start-otbr`) starts the OTBR container with `otbr_start.sh`;
3.  creates network 2 on the OTBR: a fresh random dataset on a channel other
    than network 1's (default 25, or 20 if network 1 uses 25), or the one in
    `THREAD2_DATASET_HEX`;
4.  adds an on-mesh prefix (`fd11:<first 4 hex digits of extpanid>::/64`),
    registers it and enables the SRP server;
5.  checks that the OTBR is `leader`, the SRP server is `running` and the
    network data has a DNS/SRP service;
6.  writes `~/cnet412_config.json` (dataset 1 as the Thread network, dataset 2 as
    the PIXIT) and starts `th-cli run-tests --tests-list TC_CNET_4_12`.

Environment variables (optional): `THREAD2_DATASET_HEX`, `THREAD2_CHANNEL`,
`OTBR_ON_MESH_PREFIX`, `INFRA_IFACE`, `OTBR_CONTAINER`, `CONFIG_FILE`,
`QR_CODE`. See `--help`.

### Questions asked by `th-cli`

Answer them **in the terminal where `th-cli` runs**. Each question times out
after 60 seconds, which cancels the run.

| Question                                                  | Answer                    |
| --------------------------------------------------------- | ------------------------- |
| `Do you want to reuse the previous commissioning information?` | `2` (NO)                  |
| `Make sure the DUT is in Commissioning Mode`              | `1` (DONE)                |

Reset the DUT right before the run: BLE advertising is time limited on many
devices. A successful run takes about 3 minutes and ends with
`Test Case Completed [PASSED]: TC-CNET-4.12`. The log is in `~/output_logs/`.

The DUT is commissioned after the run: **factory reset it before the next run**.
Do not kill `th-cli` with `pkill`; use `th-cli abort-testing`.

## Why the config sets `rcp_serial_path` to `null`

`th-cli` merges your config into the backend's default project config. That
default contains a full `network.thread` block, so a file with only
`operational_dataset_hex` is still parsed as `ThreadAutoConfig`, and the backend
would start its own OTBR with a dataset generated at suite start. That dataset
cannot be put into the PIXIT in advance. Setting `rcp_serial_path` to `null`
makes the Auto validation fail, so the config is parsed as `ThreadExternalConfig`
and the OTBR started by the script is used.

## Troubleshooting

| Symptom                                                                                          | Cause / fix                                                                                             |
| ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `Prompt timed out`, all steps `CANCELLED`                                                        | A question was not answered in the `th-cli` terminal within 60 s.                                       |
| `Commissionable node discovery over BLE failed`, `le-connection-abort-by-local`, `Secure Pairing Failed` | DUT is not advertising or does not accept the BLE connection. Power-cycle it and rerun right away.      |
| Commissioning passes, then 3x `CASESession ... Timeout`                                          | The TH has no IPv6 route to network 1. Put the TH on the border router's LAN.                          |
| Step 7: `SRV for '<fabric>-<node>._matter._tcp.local.' not found`                                | OTBR for network 2 is not running or its SRP server is off. Check `ot-ctl state`, `srp server state`.   |
| Script: `OTBR state is 'child'`                                                                  | Another node holds a partition with the same dataset (a leftover DUT). Reset the DUT.                   |
| `Test runner is not IDLE`                                                                        | A previous run died with a question open. Run `th-cli abort-testing`.                                   |
| Backend starts its own OTBR                                                                      | `rcp_serial_path` is not `null` in the config (see above).                                              |

## Known issues

-   `otbr_start.sh` may mount an `avahi` directory that no longer exists, so the
    container starts with an empty `/etc/avahi`. Check with
    `docker exec otbr-chip ls /etc/avahi`. The script prints a warning. Fix:

    ```bash
    sed -i 's#backend/app/otbr_manager/avahi#backend/test_collections/matter/sdk_tests/support/otbr_manager/avahi#' \
      ~/certification-tool/backend/test_collections/matter/scripts/OTBR/otbr_start.sh
    ```

-   `otbr_start.sh` starts a default fixed network (extended PAN ID
    `5b35dead5b35beef`, network key `00112233445566778899aabbccddeeff`) before
    the script replaces it. Its on-mesh prefix `fd11:35::/64` can stay in the
    network data. It does not affect the test.
-   Several TH in one place: use generated datasets (the default), and never
    let two TH share a DUT, a channel or an external border router. Two OTBRs
    with the same network key and extended PAN ID merge into one partition.

## Verification status

Checked on one TH (Wi-Fi uplink, RCP dongle), one EFR32 DUT and one external
border router (GL.iNet GL-S200): three consecutive passing runs with a freshly
generated dataset 2 each time. Not checked: more than one TH or DUT, other
border routers, the fixed-dataset mode on the current TH.

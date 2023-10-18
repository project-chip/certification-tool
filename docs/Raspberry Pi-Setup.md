<!--
 *
 * Copyright (c) 2023 Project CHIP Authors
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
-->

# Setup Raspberry Pi For Certification Use with Test Harness

The following will document how to setup a Raspberry Pi so it can be used for certification with Test Harness and all configuration.

## Requirements

-   SD card 64 GB or more
-   RaspberryPi 4 or newer with at least 4 GB RAM
-   Internet access on Raspberry Pi during setup.

1. Download and flash a micro SD-card with [Ubuntu Server 22.04](https://ubuntu.com/download/raspberry-pi/thank-you?version=22.04&architecture=server-arm64+raspi) for Raspberry Pi using [Raspberry Pi imager](https://www.raspberrypi.com/software/)

2. If needed, configure WiFi ([Ubuntu guide](https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi#3-wifi-or-ethernet))

3. Boot Ubuntu 22.04 on Raspberry Pi
4. SSH into the Raspberry Pi:

    ```
    ssh ubuntu@<pi-ip-address>
    ```

    - Default password is `ubuntu` must be changed.
    - If you don't know the IP address you can discover it from another machine on the LAN:
        - On Linux and macOS (might require `net-tools` installed)
            ```
            arp -na | grep -i  "b8:27:eb\|dc:a6:32\|e4:5f:01"
            ```
        - On Windows:
            ```
            arp -a | findstr b8-27-eb dc-a6-32 e4-5f-01
            ```

5. Setup `ssh` key with github

    Either of these works:

    - Copy existing GitHub registered `ssh` keys to `~/.ssh` on Raspberry Pi
    - Create new key
        - `ssh-keygen -t rsa -C "<your github email>"`
        - and public key to [GitHub Profile](https://github.com/settings/ssh/new)

6. Clone Test Harness code:

    ```
    git clone git@github.com:project-chip/certification-tool.git
    ```

7. Start auto install

    Note this script takes about 1 hour to run and will reboot the machine in the end.

    Run the following inside `certification-tool` folder:

    ```
    ./scripts/pi-setup/auto-install.sh
    ```

    This script will:

    - Install all dependencies
    - Configure Machine
    - Pull Test Harness Code
    - Install Matter sample apps

8. Wait for 5-10 minutes for the test harness to startup, then access it from a browser

    `http://<rpi-ip>`

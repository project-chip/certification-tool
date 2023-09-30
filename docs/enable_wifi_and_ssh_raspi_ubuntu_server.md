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

### By default, wifi is disabled in Ubuntu Server, we need the below way to enable WiFi on Raspberry Pi.

_This manual assumes you have a Raspberry Pi connected to monitor with a keyboard._

_There is a way to modify the sd card's files directly after flashing to enable wifi once you put it in your raspi. But finding the IP address to SSH to will be tricky unless you have very few devices on your intended network._

_(also... please replace vim with you favorite text editor in the following steps!)_

# Create a network plan with your intended wifi's SSID and password:

1. `sudo vim /etc/netplan/50-cloud-init.yaml`

2. Delete the contents of the file if there is any.

3. Paste the following into the file before saving+closing it; making sure to replacing `<wifi-ssid>` & `<wifi-password>`:

```
network:
    ethernets:
        eth0:
            dhcp4: true
            match:
                driver: bcmgenet smsc95xx lan78xx
            optional: true
            set-name: eth0
    version: 2
    wifis:
        wlan0:
            optional: true
            access-points:
                "<wifi-ssid>":
                    password: "<wifi-password>"
            dhcp4: true
```

4. `$ sudo netplan -debug generate`
5. `$ sudo reboot`

_Pro Tip: To change wifi networks in the future, edit the `<wifi-ssid>` & `<wifi-password>` and reboot the Raspberry Pi._

## Enable WiFi supplicant permission in Ubuntu server:

By default, wpa_supplicant is not allowed to update (overwrite) configurations, if you want chip app to be able to store the configuration changes permanently, we need to make the following changes:

6. Edit `dbus-fi.w1.wpa_supplicant1.service` to use our own conf file instead:

`$ sudo vim /etc/systemd/system/dbus-fi.w1.wpa_supplicant1.service`

7. Change the wpa_supplicant start parameter to match the following, then save+close the file:

`ExecStart=/sbin/wpa_supplicant -u -s -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf`

8. Create the wpa-supplicant conf file:

` $ sudo vim /etc/wpa_supplicant/wpa_supplicant.conf`

9. Paste the following into the new file before saving+closing the file:

```
ctrl_interface=DIR=/run/wpa_supplicant
update_config=1
```

10. `$ sudo reboot`

After reboot your Raspberry Pi should be connected to the wifi-network you specified in step 4.

11. Remove any eth cables and run `$ ping 8.8.8.8` to make sure you are connected to the wifi network and online!

_TROUBLESHOOTING: If this doesn't work, revisit the prior steps double checking you got the SSID and password correct._

## SSHing to your Raspberry Pi over wifi

12. Enable ssh on the Raspberry Pi by running `$ sudo raspi-config` _(you may need to intall it)_.

13. In the `raspi-config` GUI Navigate to `Interfacte Option` --> `SSH` --> `<Yes>` --> `<Ok>` --> `<Finish>`

14. Run `$ hostname -I` on the raspi after reboot to get the ip of the Raspberry Pi on your network.

15. While on the same network (via wifi or eth) as the Raspberry Pi, run `$ ssh ubuntu@<ip-address-given-by-hostname>` from your computer.

16. Hopefully you're in!

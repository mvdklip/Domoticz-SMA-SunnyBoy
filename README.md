# Domoticz-SMA-SunnyBoy
Domoticz plugin to get SMA Sunny Boy information

Tested with Python version 3.7, Domoticz versions 4.10717, 4.11799, 2020.1 and 2020.2

## Installation

Assuming that domoticz directory is installed in your home directory.

```bash
cd ~/domoticz/plugins
git clone https://github.com/rklomp/Domoticz-SMA-SunnyBoy
# restart domoticz:
sudo systemctl restart domoticz
```
In the web UI, navigate to the Hardware page. In the hardware dropdown there will be an entry called "SMA Sunny Boy".

Make sure to (temporarily) enable 'Accept new Hardware Devices' in System Settings so that the plugin can add devices.

## Known issues

## Updating

Like other plugins, in the Domoticz-SMA-SunnyBoy directory:
```bash
git pull
sudo /etc/init.d/domoticz.sh restart
```

## Parameters

| Parameter | Value |
| :--- | :--- |
| **IP address** | IP of the SMA Sunny Boy eg. 192.168.1.231 |
| **Password** | password for the User Group, not the Installer one |
| **Query interval** | how often is data retrieved from the SMA |
| **Debug** | show debug logging |

## Acknowledgements

Based on the scripts found here

https://github.com/merlot-dev/Domoticz-SMA-SunnyBoy \
https://community.openhab.org/t/example-on-how-to-access-data-of-a-sunny-boy-sma-solar-inverter/50963/19



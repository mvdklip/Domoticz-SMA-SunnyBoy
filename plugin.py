# SMA Sunny Boy Python Plugin for Domoticz
#
# Authors: merlot, rklomp
#
# Based on https://github.com/merlot-dev/Domoticz-SMA-SunnyBoy

"""
<plugin key="SMASunnyBoy" name="SMA Sunny Boy Solar Inverter" author="rklomp" version="1.0.3">
    <description>
        <h2>SMA Sunny Boy Solar Inverter Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Register instant power and daily generated energy</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true"/>
        <param field="Password" label="User group password" width="200px" required="true" password="true"/>
        <param field="Mode3" label="Query interval" width="75px" required="true">
            <options>
                <option label="5 sec" value="1"/>
                <option label="15 sec" value="3"/>
                <option label="30 sec" value="6"/>
                <option label="1 min" value="12" default="true"/>
                <option label="3 min" value="36"/>
                <option label="5 min" value="60"/>
                <option label="10 min" value="120"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true"/>
            </options>
        </param>
    </params>
</plugin>
"""

import requests
import Domoticz


class BasePlugin:
    enabled = False
    lastPolled = 0
    loginSid = None
    baseUrl = None
    headers = {'Content-Type': 'application/json', 'Accept-Charset': 'UTF-8'}
    maxAttempts = 3

    def __init__(self):
        return

    def login(self, force=False):
        if not force and self.loginSid is not None:
            return self.loginSid

        try:
            url = "%s/login.json" % self.baseUrl
            payload = '{"pass" : "%s", "right" : "usr"}' % Parameters["Password"]
            r = requests.post(url, data=payload, headers=self.headers, verify=False)
        except Exception as e:
            Domoticz.Log("Error accessing SMA inverter on %s; %s" % (Parameters["Address"], e))
        else:
            j = r.json()
            try:
                sid = j['result']['sid']
                if sid is None:
                    Domoticz.Error("Unable to login to SMA inverter on %s using supplied password" % Parameters["Address"])
                self.loginSid = sid
                Domoticz.Status("Successfully logged in to SMA inverter on %s" % Parameters["Address"])
                Domoticz.Debug("Received SID: %s" % sid)
                return self.loginSid
            except:
                Domoticz.Log("No valid response from SMA inverter on %s; %s" % (Parameters["Address"], j))

    def logout(self):
        Domoticz.Status("Closing session to SMA inverter on %s" % Parameters["Address"])

        url = "%s/logout.json?sid=%s" % (self.baseUrl, self.loginSid)
        r = requests.post(url, data="{}", headers=self.headers, verify=False)
        Domoticz.Debug(r.text)

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
        else:
            Domoticz.Debugging(0)

        if len(Devices) == 0:
            Domoticz.Device(Name="PV Generation", Unit=1, Type=243, Subtype=29, Switchtype=4).Create()
            Domoticz.Device(Name="kWh total", Unit=2, TypeName="Custom", Options={"Custom": "1;kWh"}).Create()

        DumpConfigToLog()

        self.baseUrl = "https://%s/dyn" % Parameters["Address"]
        self.login()

        Domoticz.Heartbeat(5)

    def onStop(self):
        Domoticz.Debug("onStop called")
        self.logout()

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called %d" % self.lastPolled)

        if self.lastPolled == 0:
            attempt = 1
            relogin = False

            while True:
                if 1 < attempt < self.maxAttempts:
                    Domoticz.Debug("Previous attempt failed, trying new login...")
                    relogin = True
                if attempt >= self.maxAttempts:
                    Domoticz.Error("Failed to retrieve data from %s, cancelling..." % Parameters["Address"])
                    break
                attempt += 1

                sid = self.login(relogin)
                url = "%s/getValues.json?sid=%s" % (self.baseUrl, sid)
                payload = '{"destDev":[],"keys":["6400_00260100","6100_40263F00"]}'

                try:
                    r = requests.post(url, data=payload, headers=self.headers, verify=False)
                    j = r.json()
                except Exception as e:
                    Domoticz.Log("No data from SMA inverter on %s; %s" % (Parameters["Address"], e))
                else:
                    Domoticz.Debug("Received data: %s" % j)
                    if "err" in j:
                        continue

                    result = list(j['result'].values())[0]
                    sma_pv_watt = result['6100_40263F00']['1'][0]['val']
                    sma_kwh_total = result['6400_00260100']['1'][0]['val']

                    if sma_pv_watt is None:
                        sma_pv_watt = 0

                    if sma_kwh_total is None:
                        Domoticz.Log("Received data from %s, but values are None" % Parameters["Address"])
                        break

                    Devices[1].Update(nValue=0, sValue=str(sma_pv_watt)+";"+str(sma_kwh_total))
                    svalue = "%.2f" % (sma_kwh_total/1000)
                    Devices[2].Update(nValue=0, sValue=svalue.replace('.', ','))
                    break

        self.lastPolled += 1
        self.lastPolled %= int(Parameters["Mode3"])


global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

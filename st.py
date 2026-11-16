"""Minimal SmartThings client for the two Samsung ACs."""
import json, os, sys, urllib.request
TOKEN = open(os.path.expanduser("~/.config/smartthings/token")).read().strip()
DEV = json.load(open(os.path.expanduser("~/.config/smartthings/devices.json")))  # {"sala": "<deviceId>", "quarto": "<deviceId>"}
API = "https://api.smartthings.com/v1/devices/"

def _req(url, body=None):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                               headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=20))

def status(room):
    m = _req(API + DEV[room] + "/status")["components"]["main"]
    g = lambda c, a: m.get(c, {}).get(a, {}).get("value")
    pc = g("powerConsumptionReport", "powerConsumption") or {}
    return {"switch": g("switch", "switch"), "mode": g("airConditionerMode", "airConditionerMode"),
            "setpoint": g("thermostatCoolingSetpoint", "coolingSetpoint"), "fan": g("airConditionerFanMode", "fanMode"),
            "ac_temp": g("temperatureMeasurement", "temperature"), "autoclean": g("custom.autoCleaningMode", "autoCleaningMode"),
            "clean_state": g("custom.autoCleaningMode", "operatingState"), "opt": g("custom.airConditionerOptionalMode", "acOptionalMode"),
            "energy_wh": pc.get("energy"), "power_w": pc.get("power")}

def cmd(room, capability, command, *args):
    return _req(API + DEV[room] + "/commands",
                {"commands": [{"component": "main", "capability": capability, "command": command, "arguments": list(args)}]})

def apply(room, mode=None, setpoint=None, fan=None, on=None, autoclean=None, opt=None):
    if autoclean is not None: cmd(room, "custom.autoCleaningMode", "setAutoCleaningMode", autoclean)
    if on is True: cmd(room, "switch", "on")
    if mode: cmd(room, "airConditionerMode", "setAirConditionerMode", mode)
    if setpoint is not None: cmd(room, "thermostatCoolingSetpoint", "setCoolingSetpoint", setpoint)
    if fan: cmd(room, "airConditionerFanMode", "setFanMode", fan)
    if opt: cmd(room, "custom.airConditionerOptionalMode", "setAcOptionalMode", opt)
    if on is False: cmd(room, "switch", "off")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        for r in DEV: print(r, status(r))
    else:  # st.py quarto mode=dry setpoint=18 on=1
        kw = {}
        for a in sys.argv[2:]:
            k, v = a.split("=")
            kw[k] = (v == "1") if k == "on" else int(v) if k == "setpoint" else v
        apply(sys.argv[1], **kw); print(sys.argv[1], status(sys.argv[1]))

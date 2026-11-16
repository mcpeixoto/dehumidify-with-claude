"""Decode SwitchBot Meter Pro CO2 adverts from ble.jsonl -> readings."""
import json, sys, math, datetime as dt

def decode(mfr_hex):
    b = bytes.fromhex(mfr_hex)[2:]  # drop company id 0x0969
    if len(b) < 15: return None
    t = (b[9] & 0x7F) + (b[8] & 0x0F) / 10
    if not b[9] & 0x80: t = -t
    rh = b[10] & 0x7F
    co2 = int.from_bytes(b[13:15], "big")
    return t, rh, co2

def dewpoint(t, rh):
    a, c = 17.62, 243.12
    g = math.log(rh / 100) + a * t / (c + t)
    return c * g / (a - g)

def abs_hum(t, rh):  # g/m3
    return 6.112 * math.exp(17.67 * t / (t + 243.5)) * rh * 2.1674 / (273.15 + t)

def readings(path="ble.jsonl"):
    last = None
    for line in open(path):
        o = json.loads(line)
        if not o.get("mfr"): continue
        r = decode(o["mfr"])
        if r and r != last:
            last = r
            yield o["ts"], *r

if __name__ == "__main__":
    rows = list(readings())
    for ts, t, rh, co2 in rows[-int(sys.argv[1]) if len(sys.argv) > 1 else -20:]:
        print(f"{dt.datetime.fromtimestamp(ts):%H:%M:%S}  {t:5.1f}C  RH {rh:3d}%  CO2 {co2:4d}  dew {dewpoint(t, rh):4.1f}C  abs {abs_hum(t, rh):4.1f} g/m3")

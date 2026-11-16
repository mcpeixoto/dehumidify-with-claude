"""Every 60 s: latest sensor reading + both AC states -> climate.csv"""
import csv, time, datetime as dt, os
from decode import decode, dewpoint, abs_hum
import json, st
F = "climate.csv"
def last_reading():
    with open("ble.jsonl","rb") as f:
        f.seek(max(0, os.path.getsize("ble.jsonl") - 20000)); lines = f.read().decode(errors="ignore").splitlines()
    for l in reversed(lines):
        try: o = json.loads(l)
        except Exception: continue
        if o.get("mfr") and (r := decode(o["mfr"])): return o["ts"], r
if __name__ == "__main__":
    new = not os.path.exists(F)
    w = csv.writer(open(F, "a", buffering=1))
    if new: w.writerow(["time","temp","rh","co2","dew","abs_gm3"] + [f"{r}_{k}" for r in st.DEV for k in ["switch","mode","setpoint","fan","ac_temp","power_w","energy_wh","clean_state"]])
    while True:
        try:
            ts, (t, rh, co2) = last_reading()
            row = [dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), t, rh, co2, round(dewpoint(t, rh),1), round(abs_hum(t, rh),2)]
            for r in st.DEV:
                s = st.status(r); row += [s[k] for k in ["switch","mode","setpoint","fan","ac_temp","power_w","energy_wh","clean_state"]]
            w.writerow(row)
        except Exception as e:
            print("err", e, flush=True)
        time.sleep(60)

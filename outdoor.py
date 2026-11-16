"""Every 15 min: outdoor weather near Oeiras (Open-Meteo) -> outdoor.csv"""
import csv, json, os, time, urllib.request, math
URL = ("https://api.open-meteo.com/v1/forecast?latitude=38.71&longitude=-9.30"
       "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation&timezone=Europe%2FLisbon")
F = "outdoor.csv"
ah = lambda t, rh: 6.112 * math.exp(17.67 * t / (t + 243.5)) * rh * 2.1674 / (273.15 + t)
new = not os.path.exists(F)
w = csv.writer(open(F, "a", buffering=1))
if new: w.writerow(["time", "temp", "rh", "abs_gm3", "wind_kmh", "precip_mm"])
while True:
    try:
        c = json.load(urllib.request.urlopen(URL, timeout=20))["current"]
        w.writerow([c["time"].replace("T", " "), c["temperature_2m"], c["relative_humidity_2m"],
                    round(ah(c["temperature_2m"], c["relative_humidity_2m"]), 2), c["wind_speed_10m"], c["precipitation"]])
    except Exception as e:
        print("err", e, flush=True)
    time.sleep(900)

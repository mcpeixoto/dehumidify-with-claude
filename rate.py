"""rate.py START END -> abs humidity change/hour, temp change, energy used (sala)."""
import csv, sys, datetime as dt
rows = list(csv.DictReader(open("climate.csv")))
p = lambda s: dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
a, b = (dt.datetime.strptime(x, "%Y-%m-%d %H:%M") for x in sys.argv[1:3])
w = [r for r in rows if a <= p(r["time"]) <= b]
r0, r1 = w[0], w[-1]; h = (p(r1["time"]) - p(r0["time"])).total_seconds() / 3600
d = float(r1["abs_gm3"]) - float(r0["abs_gm3"])
e = sum(int(r1[f"{k}_energy_wh"]) - int(r0[f"{k}_energy_wh"]) for k in ("sala", "quarto"))
print(f"{r0['time']}→{r1['time']}  abs {r0['abs_gm3']}→{r1['abs_gm3']} ({d/h:+.2f} g/m3/h)  T {r0['temp']}→{r1['temp']}  RH {r0['rh']}→{r1['rh']}  energy {e} Wh ({e/h:.0f} W avg)")

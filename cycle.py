"""Alternate both ACs between HEAT and DRY, switching on the sala sensor temperature.

The units share one outdoor unit: heat is locked out while either is drying,
so the house can't be heated and dried at once. Instead:
  HEAT both (setpoint HEAT_SP) until sala >= HI, then DRY both (18°C) until sala <= LO.
"""
import sys, time, datetime as dt
import st
from logger import last_reading  # noqa: E402  (logger module guards its loop)

HI, LO, HEAT_SP = (float(x) for x in (sys.argv[1:4] if len(sys.argv) > 3 else (21.5, 19.5, 24)))
ROOMS = ("sala", "quarto")

def log(msg):
    line = f"{dt.datetime.now():%F %T} cycle: {msg}"
    print(line, flush=True); open("experiments.log", "a").write(line + "\n")

def set_all(mode, sp):
    for r in ROOMS:
        st.cmd(r, "airConditionerMode", "setAirConditionerMode", mode)
    time.sleep(10)
    for r in ROOMS:
        st.cmd(r, "thermostatCoolingSetpoint", "setCoolingSetpoint", sp)

phase = None
log(f"start HI={HI} LO={LO} heat_sp={HEAT_SP}")
while True:
    try:
        _, (t, rh, co2) = last_reading()
        want = phase
        if phase is None: want = "heat" if t < HI else "dry"
        elif phase == "heat" and t >= HI: want = "dry"
        elif phase == "dry" and t <= LO: want = "heat"
        if want != phase:
            if phase == "dry":
                # Off, not fan: a fan over the wet coil blows the condensate back into the room.
                # 10 min lets the tray drain and releases the heat lock (shared outdoor unit).
                for r in ROOMS: st.cmd(r, "switch", "off")
                log(f"dry -> off (drain) at {t}C RH {rh}%"); time.sleep(600)
                for r in ROOMS: st.cmd(r, "switch", "on")
                time.sleep(10)
            set_all(want, HEAT_SP if want == "heat" else 18)
            log(f"{phase} -> {want} at {t}C RH {rh}%")
            phase = want
    except Exception as e:
        print("err", e, flush=True)
    time.sleep(60)

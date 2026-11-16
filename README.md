# Letting Claude dehumidify my house

My flat is humid. The sensor in the living room sat at **74% relative humidity**, and running the
AC in "dry" mode for two hours, or heating the room first and then drying it, never seemed to help.

So I handed the problem to Claude (Claude Code, running on my Mac): read the room sensor over
Bluetooth, control both air conditioners through SmartThings, diagnose what's going on, and
iterate on AC settings until the humidity comes down. This repo holds the code it wrote and every
reading it logged.

## Hardware

- **SwitchBot Meter Pro CO2** in the living room (`sala`): temperature, humidity and CO2, read from
  its Bluetooth advertisements. No hub or cloud needed.
- **Two Samsung wall-mounted ACs** (living room `sala`, bedroom `quarto`), controlled through the
  SmartThings API.

## What it found

1. **Percent humidity hides the progress.** Drying the air also cools the room, and cooler air
   shows a *higher* percentage for the same amount of water. In the first test the water in the air
   fell 21% (13.7 → 10.8 g/m³), while the display only went 74% → 68%. So everything here is scored
   in **absolute humidity (grams of water per m³)**, not %.
2. **Dry mode with the setpoint above room temperature does nothing.** The bedroom AC was set to
   dry mode at 25°C in a 20°C room. Samsung's dry mode stops the compressor once the room is below
   the setpoint, so it was just moving air around.
3. **"Auto Clean" puts the water back.** It was on for both units. After every shutdown it runs the
   fan to dry the coil, which blows the water it just collected back into the room. It is now off
   on both.

## Experiments

Scored from the living-room sensor. `climate.csv` has the minute-by-minute data and
`experiments.log` says when each one started.

| # | Setting | Water removed | AC power |
|---|---|---|---|
| E1 | sala: dry mode, 18°C, Auto Clean off | 4.4 g/m³/h (13.7 → 10.8) | ~180 W |
| E2 | sala: cool mode, 18°C, fan low | 1.8 g/m³/h (10.7 → 10.0) | ~190 W |
| E3 | both units: dry mode, 18°C (doors open) | running | |

E2 started with drier air than E1 (less water left to pull out), so the comparison isn't perfectly
fair, but dry mode clearly did better.

## How it works

| File | What it does |
|---|---|
| `blescan.swift`, `Info.plist`, `build.sh` | A tiny macOS app that scans Bluetooth and appends SwitchBot adverts to `ble.jsonl`. It has to be an `.app`: macOS kills command-line processes that touch Bluetooth without a usage description. |
| `decode.py` | Decodes the Meter Pro CO2 advert (temperature, humidity, CO2) and computes dew point and absolute humidity. |
| `st.py` | Minimal SmartThings client: read AC status, set mode, setpoint, fan and Auto Clean. Reads the token from `~/.config/smartthings/token` and the device IDs from `~/.config/smartthings/devices.json`. |
| `logger.py` | Every minute, writes the latest sensor reading and both ACs' state to `climate.csv`. |
| `rate.py` | `python3 rate.py "YYYY-MM-DD HH:MM" "YYYY-MM-DD HH:MM"` gives the water removed per hour and the energy used over that window. |

```bash
./build.sh                     # start the Bluetooth scanner (allow Bluetooth when macOS asks)
python3 logger.py &            # log every minute
python3 st.py                  # both ACs' status
python3 st.py sala mode=dry setpoint=18 on=1 autoclean=off
```

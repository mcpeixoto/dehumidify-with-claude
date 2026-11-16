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

4. **The water doesn't leave the unit: a fan blowing over the wet coil puts it back.** Samsung's
   self-check (`samsungce.selfCheck` → `startSelfCheck`) never reported a result, but it left the
   living-room unit on fan/turbo right after a drying run. In 4 minutes the water in the air went
   **11.1 → 13.0 g/m³**, about half of what an hour of drying had removed. Every fan-only moment
   (Auto Clean, dry mode's compressor-off pauses, switching from dry to heat) returns the
   condensate to the room. The raw OCF `execute` channel accepts commands on these 2025 units but
   returns nothing, so there's no deeper service data to read.

5. **The outside air is as wet as the inside.** On 16 Nov at 19:15 it was 18.3°C and 90% outside
   (Open-Meteo, Oeiras), i.e. **14.1 g/m³**, against 15.2 g/m³ indoors. Every draught brings that air
   in, so the house drifts back to the outdoor water content, and opening windows tonight doesn't
   help. To get ~55% at 21°C the air needs ~10 g/m³, which takes continuous drying, not sessions.
6. **Warming the house releases water from walls and furniture.** During the first heating phase of
   the cycle the air went 11.1 → 15.2 g/m³ in 17 min. The air holds only ~1 kg of water; the materials
   hold tens of kg, and they give it back when warmed.

## Experiments

Scored from the living-room sensor. `climate.csv` has the minute-by-minute data and
`experiments.log` says when each one started.

| # | Setting | Water removed | AC power |
|---|---|---|---|
| E1 | sala: dry mode, 18°C, Auto Clean off | 4.4 g/m³/h (13.7 → 10.8) | ~180 W |
| E2 | sala: cool mode, 18°C, fan low | 1.8 g/m³/h (10.7 → 10.0) | ~190 W |
| E3 | both units: dry mode, 18°C (doors open) | **+4.8 g/m³/h**, humidity rose (10.0 → 10.8 in 10 min) | ~200 W |
| E4 | both units alternate: heat to 21.5°C, then dry down to 19.5°C (`cycle.py`) | **stopped**: heating took the air 11.1 → 15.2 g/m³ in 17 min | |
| E5 | both units: continuous dry, 18°C | running | |

E2 started with drier air than E1 (less water left to pull out), so the comparison isn't perfectly
fair, but dry mode clearly did better.

E3 went backwards because the doors were opened when I got home: humid bedroom air mixed into the
living room, which had been dried on its own until then. The bedroom was holding a lot of the water.

**Heating and drying at the same time is impossible on this system.** While either unit is in dry or
cool mode, SmartThings drops `heat` from both units' available modes. They share one outdoor unit
(multi-split), and it can only run one direction at a time. Drying in winter cools the house, so E4
alternates instead: heat until the living room hits 21.5°C, then dry until it falls to 19.5°C.

## How it works

| File | What it does |
|---|---|
| `blescan.swift`, `Info.plist`, `build.sh` | A tiny macOS app that scans Bluetooth and appends SwitchBot adverts to `ble.jsonl`. It has to be an `.app`: macOS kills command-line processes that touch Bluetooth without a usage description. |
| `decode.py` | Decodes the Meter Pro CO2 advert (temperature, humidity, CO2) and computes dew point and absolute humidity. |
| `st.py` | Minimal SmartThings client: read AC status, set mode, setpoint, fan and Auto Clean. Reads the token from `~/.config/smartthings/token` and the device IDs from `~/.config/smartthings/devices.json`. |
| `logger.py` | Every minute, writes the latest sensor reading and both ACs' state to `climate.csv`. |
| `cycle.py` | `python3 cycle.py 21.5 19.5 24`: alternates both ACs between heat and dry, switching on the living-room temperature. |
| `outdoor.py` | Every 15 min, logs outdoor temperature and humidity (Open-Meteo) to `outdoor.csv`. |
| `rate.py` | `python3 rate.py "YYYY-MM-DD HH:MM" "YYYY-MM-DD HH:MM"` gives the water removed per hour and the energy used over that window. |

```bash
./build.sh                     # start the Bluetooth scanner (allow Bluetooth when macOS asks)
python3 logger.py &            # log every minute
python3 st.py                  # both ACs' status
python3 st.py sala mode=dry setpoint=18 on=1 autoclean=off
```

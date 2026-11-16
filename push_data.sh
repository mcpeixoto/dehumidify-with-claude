#!/usr/bin/env bash
# Commit and push new sensor data every 30 min.
cd "$(dirname "$0")"
while true; do
  sleep 1800
  git add climate.csv experiments.log
  git diff --cached --quiet || { git commit -q -m "data: $(date '+%F %H:%M') readings"; git push -q; }
done

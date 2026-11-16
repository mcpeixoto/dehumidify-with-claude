#!/usr/bin/env bash
# Build and launch the BLE scanner as a tiny .app bundle.
# macOS kills plain CLI processes that touch Bluetooth (no NSBluetoothAlwaysUsageDescription),
# so the scanner lives in its own bundle and is started with `open`, which triggers the permission prompt.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p BLEScan.app/Contents/MacOS
cp Info.plist BLEScan.app/Contents/Info.plist
swiftc -O blescan.swift -o BLEScan.app/Contents/MacOS/blescan
codesign -s - --force BLEScan.app
open BLEScan.app

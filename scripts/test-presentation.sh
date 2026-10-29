#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
python3 scripts/install.py --build-only
xcrun clang -fobjc-arc -framework AppKit tests/presentation_check.m -o .build/presentation-check
export WINDOWS_STEAM_PRESENTATION=1
export DYLD_INSERT_LIBRARIES="$PWD/.build/WindowsSteamPresentation.dylib"
.build/presentation-check 'C:\Program Files (x86)\Steam\Steam.exe' hidden
.build/presentation-check 'C:\Program Files (x86)\Steam\bin\steamwebhelper.exe' hidden
.build/presentation-check '/Applications/Example.app/Contents/MacOS/Sikarugir' hidden
.build/presentation-check 'C:\Games\DifferentGame.exe' visible

.build/presentation-check 'wine64-preloader' late

#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -r requirements-build.txt

rm -rf build
chmod -R u+w dist 2>/dev/null || true
rm -rf dist
pyinstaller --noconfirm register_delay.spec

if [[ ! -d dist/RegisterDelay/_internal/customtkinter ]]; then
  echo "ERROR: customtkinter was not bundled. Did you activate the venv?" >&2
  exit 1
fi

if [[ "$(uname)" == "Darwin" ]]; then
  ditto -c -k --sequesterRsrc --keepParent dist/RegisterDelay.app dist/RegisterDelay-macOS.zip
  echo "Built dist/RegisterDelay.app"
  echo "Zip:  dist/RegisterDelay-macOS.zip"
  echo "Open: open dist/RegisterDelay.app"
else
  echo "Built dist/RegisterDelay.exe"
fi

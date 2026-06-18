# Register Delay

Converts GE PLC ladder logic CSVs so `TMR_TENTHS` timers use register-based presets instead of hardcoded values, and adds first-scan `MOVE_INT` init rungs.

## Option 1: Download the Windows app (recommended)

Pre-built executables are published on [GitHub Releases](https://github.com/kartersanamo/RegisterDelay/releases).

1. Open the [latest release](https://github.com/kartersanamo/RegisterDelay/releases/latest).
2. Download `RegisterDelay.exe` from the **Assets** section.
3. Run it — no Python install required.

> Windows may show SmartScreen for unsigned apps. Choose **More info → Run anyway** if you trust this repo.

New releases are built automatically when a version tag is pushed (for example `v1.0.0`).

## Option 2: Run from source

Requires Python 3.10+ with Tkinter (included with the standard Python installer on Windows and macOS).

```bash
git clone https://github.com/kartersanamo/RegisterDelay.git
cd RegisterDelay
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python3 register_delay.py
```

### Use

1. Click **Choose CSV…** and pick your ladder logic export.
2. Click **Convert**.
3. Open the new file saved next to the original as `<name>_converted.csv`.

Preset registers use timer register − 5, with up to 3 `MOVE_INT` blocks per init rung.

## Option 3: Build an executable with PyInstaller

Build on the platform you want to run on. PyInstaller produces a Windows `.exe` only when run on Windows.

### Windows

```bash
git clone https://github.com/kartersanamo/RegisterDelay.git
cd RegisterDelay
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-build.txt
pyinstaller --noconfirm register_delay.spec
```

The executable is written to `dist\RegisterDelay.exe`.

### macOS / Linux

Same steps as above (use `source .venv/bin/activate` on macOS/Linux). The output is `dist/RegisterDelay` (no `.exe` extension).

### Publish a GitHub release

Tag a version and push — CI builds `RegisterDelay.exe` and attaches it to the release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow is defined in [`.github/workflows/release.yml`](.github/workflows/release.yml).

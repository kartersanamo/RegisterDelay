# Register Delay

Converts GE PLC ladder logic CSVs so `TMR_TENTHS` timers use register-based presets instead of hardcoded values, and adds first-scan `MOVE_INT` init rungs.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 register_delay.py
```

## Use

1. Click **Choose CSV…** and pick your ladder logic export.
2. Click **Convert**.
3. Open the new file saved next to the original as `<name>_converted.csv`.

That's it. Preset registers use timer register − 5, with up to 3 `MOVE_INT` blocks per init rung.

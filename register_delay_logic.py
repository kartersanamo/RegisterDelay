"""Core conversion logic for Register Delay."""

from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field

PRESET_REGISTER_OFFSET = 5
MOVES_PER_RUNG = 3
DEFAULT_DELAY_FOR_EXISTING = 30

HARDCODED_TIMER_PATTERN = re.compile(
    r"(TMR_TENTHS R)(\d+)(,G,%R\2 )(\d+)( \*\*;)"
)
REGISTER_TIMER_PATTERN = re.compile(
    r"TMR_TENTHS R(\d+),G,%R\1 R(\d+),G,%R\2 \*\*;"
)
FST_SCN_ROW_PATTERN = re.compile(r"#FST_SCN|MOVE_INT")
INSTRUCTIONAL_ROW_PATTERN = re.compile(
    r"^\s*(?:\(explain text|We need to make|This just show)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TimerChange:
    timer_register: int
    preset_register: int
    delay: int
    status: str


@dataclass
class ConversionResult:
    output_rows: list[list[str]]
    changes: list[TimerChange] = field(default_factory=list)
    init_registers: dict[int, int] = field(default_factory=dict)
    init_rungs_added: int = 0


def preset_register_for_timer(timer_register: int) -> int:
    return timer_register - PRESET_REGISTER_OFFSET


def convert_timer_cell(cell: str) -> tuple[str, int, int] | None:
    match = HARDCODED_TIMER_PATTERN.search(cell)
    if not match:
        return None

    prefix, timer_text, middle, delay_text, suffix = match.groups()
    timer_register = int(timer_text)
    default_delay = int(delay_text)
    preset_register = preset_register_for_timer(timer_register)
    replacement = f"R{preset_register},G,%R{preset_register}"
    return f"{prefix}{timer_text}{middle}{replacement}{suffix}", preset_register, default_delay


def extract_existing_preset(cell: str) -> tuple[int, int] | None:
    match = REGISTER_TIMER_PATTERN.search(cell)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def build_fst_scn_rung(moves: list[tuple[int, int]]) -> str:
    cells = ['"NOCON #FST_SCN,G,%S00001;"']
    for index, (register, delay) in enumerate(moves):
        if index > 0:
            cells.extend(["H_WIRE;", "H_WIRE;"])
        cells.append(f'"MOVE_INT 1 {delay} R{register},G,%R{register};"')
    cells.append("END_RUNG;")
    return ",".join(cells)


def build_fst_scn_rungs(register_defaults: dict[int, int]) -> list[str]:
    if not register_defaults:
        return []

    sorted_registers = sorted(register_defaults)
    rungs: list[str] = []
    for start in range(0, len(sorted_registers), MOVES_PER_RUNG):
        chunk = sorted_registers[start : start + MOVES_PER_RUNG]
        moves = [(register, register_defaults[register]) for register in chunk]
        rungs.append(build_fst_scn_rung(moves))
    return rungs


def is_fst_scn_row(row: list[str]) -> bool:
    return bool(FST_SCN_ROW_PATTERN.search(",".join(row)))


def is_instructional_row(row: list[str]) -> bool:
    return bool(row and row[0].strip() and INSTRUCTIONAL_ROW_PATTERN.match(row[0]))


def process_csv_text(csv_text: str) -> ConversionResult:
    input_rows = list(csv.reader(io.StringIO(csv_text)))

    output_rows: list[list[str]] = []
    changes_by_preset: dict[int, TimerChange] = {}
    init_registers: dict[int, int] = {}

    for row in input_rows:
        if is_fst_scn_row(row):
            continue
        if is_instructional_row(row):
            output_rows.append(row)
            continue

        updated_row = list(row)
        for column_index, cell in enumerate(updated_row):
            conversion = convert_timer_cell(cell)
            if conversion:
                new_cell, preset_register, default_delay = conversion
                timer_register = preset_register + PRESET_REGISTER_OFFSET
                updated_row[column_index] = new_cell
                init_registers[preset_register] = default_delay
                changes_by_preset[preset_register] = TimerChange(
                    timer_register=timer_register,
                    preset_register=preset_register,
                    delay=default_delay,
                    status="Converted",
                )
                continue

            existing = extract_existing_preset(cell)
            if existing:
                timer_register, preset_register = existing
                if preset_register not in init_registers:
                    init_registers[preset_register] = DEFAULT_DELAY_FOR_EXISTING
                if preset_register not in changes_by_preset:
                    changes_by_preset[preset_register] = TimerChange(
                        timer_register=timer_register,
                        preset_register=preset_register,
                        delay=init_registers[preset_register],
                        status="Unchanged",
                    )

        output_rows.append(updated_row)

    init_rungs_added = 0
    if init_registers:
        output_rows.append([])
        init_rungs = build_fst_scn_rungs(init_registers)
        init_rungs_added = len(init_rungs)
        for rung in init_rungs:
            output_rows.append([rung])

    changes = sorted(changes_by_preset.values(), key=lambda change: change.preset_register)

    return ConversionResult(
        output_rows=output_rows,
        changes=changes,
        init_registers=init_registers,
        init_rungs_added=init_rungs_added,
    )


def rows_to_csv_text(rows: list[list[str]]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()

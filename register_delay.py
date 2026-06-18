#!/usr/bin/env python3
"""Register Delay — convert PLC timer presets to registers."""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import customtkinter as ctk

from register_delay_logic import ConversionResult, TimerChange, process_csv_text, rows_to_csv_text

APP_NAME = "Register Delay"
TABLE_COLUMNS = ("timer", "preset", "delay", "status")


class RegisterDelayApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry("680x520")
        self.minsize(560, 420)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.input_path: Path | None = None

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 8))

        ctk.CTkLabel(
            header,
            text="Timer preset → register conversion",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Pick a ladder logic CSV. Saves as <name>_converted.csv",
            text_color="gray",
        ).pack(anchor="w", pady=(2, 10))

        self.file_label = ctk.CTkLabel(header, text="No file selected", anchor="w")
        self.file_label.pack(fill="x", pady=(0, 10))

        buttons = ctk.CTkFrame(header, fg_color="transparent")
        buttons.pack(fill="x")

        ctk.CTkButton(buttons, text="Choose CSV…", width=140, command=self._choose_file).pack(
            side="left", padx=(0, 8)
        )
        self.convert_button = ctk.CTkButton(
            buttons,
            text="Convert",
            width=140,
            state="disabled",
            command=self._convert,
        )
        self.convert_button.pack(side="left")

        self.status_label = ctk.CTkLabel(
            header,
            text="Results will appear after conversion.",
            text_color="gray",
            anchor="w",
            wraplength=620,
        )
        self.status_label.pack(fill="x", pady=(12, 0))

        table_shell = ctk.CTkFrame(self)
        table_shell.pack(fill="both", expand=True, padx=20, pady=(8, 20))

        ctk.CTkLabel(
            table_shell,
            text="Changes",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        table_frame = ctk.CTkFrame(table_shell, fg_color="transparent")
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._tree = ttk.Treeview(
            table_frame,
            columns=TABLE_COLUMNS,
            show="headings",
            selectmode="browse",
        )
        self._tree.heading("timer", text="Timer")
        self._tree.heading("preset", text="Preset")
        self._tree.heading("delay", text="Delay")
        self._tree.heading("status", text="Status")
        self._tree.column("timer", width=120, anchor="center")
        self._tree.column("preset", width=120, anchor="center")
        self._tree.column("delay", width=80, anchor="center")
        self._tree.column("status", width=140, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._tree.tag_configure("converted", foreground="#1f6aa5")
        self._tree.tag_configure("unchanged", foreground="#6b7280")

    def _choose_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select ladder logic CSV",
            filetypes=[("CSV files", "*.csv")],
        )
        if not path:
            return
        self.input_path = Path(path)
        self.file_label.configure(text=str(self.input_path))
        self.convert_button.configure(state="normal")
        self.status_label.configure(
            text="Ready to convert.",
            text_color="gray",
        )
        self._clear_table()

    def _convert(self) -> None:
        if self.input_path is None or not self.input_path.is_file():
            messagebox.showerror(APP_NAME, "Choose a valid CSV file first.")
            return

        output_path = self.input_path.with_name(f"{self.input_path.stem}_converted.csv")

        try:
            result = process_csv_text(self.input_path.read_text(encoding="utf-8"))
            output_path.write_text(rows_to_csv_text(result.output_rows), encoding="utf-8")
        except (OSError, ValueError) as error:
            messagebox.showerror(APP_NAME, str(error))
            return

        self._show_results(result, output_path)

    def _show_results(self, result: ConversionResult, output_path: Path) -> None:
        converted = sum(1 for change in result.changes if change.status == "Converted")
        unchanged = len(result.changes) - converted
        self.status_label.configure(
            text=(
                f"Saved to {output_path.name} — "
                f"{converted} converted, {unchanged} unchanged, "
                f"{result.init_rungs_added} init rung(s) added."
            ),
            text_color=("gray10", "gray90"),
        )
        self._populate_table(result.changes)

    def _clear_table(self) -> None:
        self._tree.delete(*self._tree.get_children())

    def _populate_table(self, changes: list[TimerChange]) -> None:
        self._clear_table()
        for change in changes:
            tag = "converted" if change.status == "Converted" else "unchanged"
            self._tree.insert(
                "",
                "end",
                values=(
                    f"%R{change.timer_register}",
                    f"%R{change.preset_register}",
                    change.delay,
                    change.status,
                ),
                tags=(tag,),
            )


def main() -> None:
    RegisterDelayApp().mainloop()


if __name__ == "__main__":
    main()

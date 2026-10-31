"""Tkinter graphical user interface for the European call option pricer."""

from __future__ import annotations

import math
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox, ttk

from black_scholes import black_scholes_call_price

APP_TITLE = "European Call Option Pricer — Black-Scholes"


@dataclass(frozen=True)
class InputField:
    """Description of one GUI input field."""

    key: str
    label: str
    default: str
    is_percentage: bool = False


INPUT_FIELDS: tuple[InputField, ...] = (
    InputField("spot", "Underlying Price (S0)", "100"),
    InputField("strike", "Strike Price (K)", "100"),
    InputField("maturity", "Time to Maturity (Years)", "1"),
    InputField("rate", "Risk-Free Interest Rate (%)", "5", is_percentage=True),
    InputField("volatility", "Volatility (%)", "20", is_percentage=True),
    InputField("dividend_yield", "Continuous Dividend Yield (%)", "0", is_percentage=True),
)


def parse_number(label: str, text: str) -> float:
    """Convert user text to a finite float, raising ``ValueError`` with a readable message."""
    cleaned = text.strip().replace(",", ".")
    if not cleaned:
        raise ValueError(f"{label}: please enter a value.")
    try:
        value = float(cleaned)
    except ValueError as exc:
        raise ValueError(f"{label}: '{text.strip()}' is not a valid number.") from exc
    if not math.isfinite(value):
        raise ValueError(f"{label}: the value must be a finite number.")
    return value


def parse_inputs(raw_values: dict[str, str]) -> dict[str, float]:
    """Parse raw GUI strings into model parameters, converting percentages to decimals."""
    parameters: dict[str, float] = {}
    for field in INPUT_FIELDS:
        value = parse_number(field.label, raw_values.get(field.key, ""))
        parameters[field.key] = value / 100.0 if field.is_percentage else value
    return parameters


class OptionPricerApp(ttk.Frame):
    """Main application frame containing the input form and the result display."""

    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=24)
        self.master = master
        self.entries: dict[str, tk.StringVar] = {}
        self.result_var = tk.StringVar(value="—")
        self.status_var = tk.StringVar(value="Enter the parameters and press Calculate.")
        self._configure_style()
        self._build_widgets()
        self.grid(row=0, column=0, sticky="nsew")

    def _configure_style(self) -> None:
        """Set fonts and theme for a clean, professional look."""
        style = ttk.Style(self.master)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 9), foreground="#555555")
        style.configure("Field.TLabel", font=("Segoe UI", 10))
        style.configure("ResultCaption.TLabel", font=("Segoe UI", 10, "bold"))
        style.configure("Result.TLabel", font=("Consolas", 18, "bold"), foreground="#0b5394")
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#555555")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(12, 6))

    def _build_widgets(self) -> None:
        """Create and lay out all widgets."""
        ttk.Label(self, text="European Call Option Pricer", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(
            self,
            text="Analytical Black-Scholes-Merton model with continuous dividend yield",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))

        form = ttk.LabelFrame(self, text="Model Parameters", padding=16)
        form.grid(row=2, column=0, columnspan=2, sticky="ew")
        form.columnconfigure(1, weight=1)

        first_entry: ttk.Entry | None = None
        for row, field in enumerate(INPUT_FIELDS):
            ttk.Label(form, text=field.label, style="Field.TLabel").grid(
                row=row, column=0, sticky="w", padx=(0, 16), pady=4
            )
            variable = tk.StringVar(value=field.default)
            entry = ttk.Entry(form, textvariable=variable, width=18, justify="right")
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            self.entries[field.key] = variable
            if first_entry is None:
                first_entry = entry

        ttk.Button(
            self,
            text="Calculate Call Price",
            style="Accent.TButton",
            command=self.calculate,
        ).grid(row=3, column=0, columnspan=2, sticky="ew", pady=16)

        result_frame = ttk.LabelFrame(self, text="Result", padding=16)
        result_frame.grid(row=4, column=0, columnspan=2, sticky="ew")
        result_frame.columnconfigure(1, weight=1)
        ttk.Label(result_frame, text="Call Price:", style="ResultCaption.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 16)
        )
        ttk.Label(result_frame, textvariable=self.result_var, style="Result.TLabel").grid(
            row=0, column=1, sticky="e"
        )

        ttk.Label(self, textvariable=self.status_var, style="Status.TLabel", wraplength=380).grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(12, 0)
        )

        self.columnconfigure(0, weight=1)
        self.master.bind("<Return>", lambda _event: self.calculate())
        if first_entry is not None:
            first_entry.focus_set()

    def calculate(self) -> None:
        """Read the inputs, price the call option and display the result or an error."""
        raw_values = {key: variable.get() for key, variable in self.entries.items()}
        try:
            parameters = parse_inputs(raw_values)
            price = black_scholes_call_price(**parameters)
        except ValueError as exc:
            self.result_var.set("—")
            self.status_var.set(f"Invalid input: {exc}")
            messagebox.showerror("Invalid Input", str(exc), parent=self.master)
            return
        self.result_var.set(f"{price:.6f}")
        self.status_var.set("Price computed with the Black-Scholes-Merton formula.")


def main() -> None:
    """Launch the Tkinter application."""
    root = tk.Tk()
    root.title(APP_TITLE)
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    OptionPricerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

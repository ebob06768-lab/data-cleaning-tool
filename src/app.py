import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

import pandas as pd


# =========================
# Project paths
# =========================
if getattr(sys, "frozen", False):
    # For the packaged EXE: keep data and reports beside the project folder.
    BASE_DIR = Path(sys.executable).resolve().parent.parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

selected_file = None
output_file = None
report_file = None


# =========================
# Theme
# =========================
BG = "#F3F6FB"
PANEL = "#FFFFFF"
NAVY = "#142B4A"
NAVY_LIGHT = "#203E63"
BLUE = "#3267E3"
BLUE_HOVER = "#2454C7"
GREEN = "#16845B"
ORANGE = "#C47A13"
RED = "#C34242"
TEXT = "#1E293B"
MUTED = "#64748B"
BORDER = "#DCE4EF"
PALE_BLUE = "#EAF0FF"
WHITE = "#FFFFFF"

# =========================
# Helpers
# =========================
def set_status(text, color=MUTED):
    status_label.config(text=text, fg=color)


def open_file(path):
    if path and Path(path).exists():
        try:
            os.startfile(str(path))
        except OSError as error:
            messagebox.showerror("Open error", str(error), parent=root)
    else:
        messagebox.showwarning(
            "File not found",
            "The file has not been created yet. Clean a data file first.",
            parent=root,
        )


def open_output_folder(path):
    if path and Path(path).exists():
        try:
            os.startfile(str(Path(path).parent))
        except OSError as error:
            messagebox.showerror("Open error", str(error), parent=root)
    else:
        messagebox.showwarning(
            "Folder not found",
            "No output is available yet. Clean a data file first.",
            parent=root,
        )


def update_card(label, value):
    label.config(text=str(value))


def trim_value(value):
    return value.strip() if isinstance(value, str) else value


# =========================
# Choose input file
# =========================
def choose_file():
    global selected_file

    filename = filedialog.askopenfilename(
        parent=root,
        title="Choose a data file",
        filetypes=[
            ("Supported data files", "*.csv *.xlsx"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
        ],
    )

    if not filename:
        return

    selected_file = Path(filename)
    file_name_label.config(text=selected_file.name)
    file_path_label.config(text=str(selected_file))
    set_status("File selected — ready to clean", GREEN)
    clean_button.config(state="normal")


# =========================
# Clean data
# =========================
def clean_data():
    global output_file, report_file

    if selected_file is None:
        messagebox.showwarning(
            "Select a file",
            "Please choose a CSV or Excel file first.",
            parent=root,
        )
        return

    clean_button.config(state="disabled")
    choose_button.config(state="disabled")
    progress_bar.start(10)
    set_status("Cleaning data… please wait", ORANGE)
    root.update_idletasks()

    try:
        if selected_file.suffix.lower() == ".csv":
            df = pd.read_csv(selected_file, dtype={"Phone": "string"})
        elif selected_file.suffix.lower() == ".xlsx":
            df = pd.read_excel(selected_file, dtype={"Phone": "string"})
        else:
            raise ValueError("Only CSV and XLSX files are supported.")

        rows_before = len(df)
        total_cells = df.shape[0] * df.shape[1]

        missing_report = {
            column: int(count)
            for column, count in df.isnull().sum().items()
            if count > 0
        }
        missing_cells = sum(missing_report.values())
        missing_percentage = (
            missing_cells / total_cells * 100 if total_cells else 0
        )

        # Trim leading and trailing spaces in text columns.
        spaces_cleaned = 0
        for column in df.columns:
            if (
                pd.api.types.is_object_dtype(df[column].dtype)
                or isinstance(df[column].dtype, pd.StringDtype)
            ):
                before = df[column].copy()
                spaces_cleaned += int(
                    before.map(
                        lambda value: (
                            len(value) - len(value.strip())
                            if isinstance(value, str)
                            else 0
                        )
                    ).sum()
                )
                df[column] = df[column].map(trim_value)

        # Standardize dates when a column named "Date" exists.
        if "Date" in df.columns:
            dates = pd.to_datetime(
                df["Date"], format="mixed", dayfirst=True, errors="coerce"
            )
            df["Date"] = dates.dt.strftime("%Y-%m-%d")

        # Basic cleanup for Egyptian mobile numbers.
        if "Phone" in df.columns:
            df["Phone"] = (
                df["Phone"]
                .astype("string")
                .str.strip()
                .str.replace(r"[\s\-]+", "", regex=True)
            )

            def fix_phone(phone):
                if pd.isna(phone):
                    return phone
                if (
                    phone.isdigit()
                    and len(phone) == 10
                    and phone.startswith(("10", "11", "12", "15"))
                ):
                    return "0" + phone
                return phone

            df["Phone"] = df["Phone"].map(fix_phone)

        df = df.drop_duplicates()
        rows_after = len(df)
        duplicates_removed = rows_before - rows_after

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        output_file = DATA_DIR / (
            f"{selected_file.stem}_cleaned{selected_file.suffix}"
        )

        if selected_file.suffix.lower() == ".xlsx":
            df.to_excel(output_file, index=False)
        else:
            df.to_csv(output_file, index=False, encoding="utf-8-sig")

        report_file = REPORTS_DIR / (
            f"{selected_file.stem}_cleaning_report.txt"
        )

        with open(report_file, "w", encoding="utf-8") as report:
            report.write("DATA CLEANING REPORT\n")
            report.write("====================\n\n")
            report.write(f"Input file: {selected_file.name}\n")
            report.write(f"Output file: {output_file.name}\n")
            report.write(f"Original rows: {rows_before}\n")
            report.write(f"Final rows: {rows_after}\n")
            report.write(f"Duplicates removed: {duplicates_removed}\n")
            report.write(f"Spaces cleaned: {spaces_cleaned}\n")
            report.write(
                f"Missing cells: {missing_cells} "
                f"({missing_percentage:.2f}%)\n\n"
            )
            report.write("Missing values by column:\n")
            if missing_report:
                for column, count in missing_report.items():
                    percentage = (
                        count / rows_before * 100 if rows_before else 0
                    )
                    report.write(
                        f"- {column}: {count} "
                        f"({percentage:.2f}% of rows)\n"
                    )
            else:
                report.write("- None\n")

        update_card(rows_before_value, f"{rows_before:,}")
        update_card(rows_after_value, f"{rows_after:,}")
        update_card(duplicates_value, f"{duplicates_removed:,}")
        update_card(missing_value, f"{missing_cells:,}")

        results_box.config(state="normal")
        results_box.delete("1.0", tk.END)
        results_box.insert(
            tk.END,
            "CLEANING COMPLETED SUCCESSFULLY\n"
            "────────────────────────────────────────\n\n"
            f"Input file       {selected_file.name}\n"
            f"Original rows    {rows_before:,}\n"
            f"Final rows       {rows_after:,}\n"
            f"Duplicates       {duplicates_removed:,}\n"
            f"Spaces cleaned   {spaces_cleaned:,}\n"
            f"Missing cells    {missing_cells:,} "
            f"({missing_percentage:.1f}% of all cells)\n\n"
            "MISSING VALUES BY COLUMN\n"
            "────────────────────────────────────────\n",
        )

        if missing_report:
            for column, count in missing_report.items():
                percentage = count / rows_before * 100 if rows_before else 0
                results_box.insert(
                    tk.END, f"• {column}: {count:,} ({percentage:.1f}% of rows)\n"
                )
        else:
            results_box.insert(tk.END, "No missing values found.\n")

        results_box.insert(
            tk.END,
            f"\nCLEANED FILE\n{output_file}\n\nREPORT\n{report_file}\n",
        )
        results_box.config(state="disabled")

        open_file_button.config(state="normal")
        open_report_button.config(state="normal")
        open_folder_button.config(state="normal")
        set_status("Cleaning completed successfully", GREEN)

        messagebox.showinfo(
            "Cleaning complete",
            "Your data has been cleaned successfully!",
            parent=root,
        )

    except Exception as error:
        set_status("Cleaning failed — check the error message", RED)
        messagebox.showerror(
            "Cleaning error",
            f"An error occurred while cleaning the file:\n\n{error}",
            parent=root,
        )
    finally:
        progress_bar.stop()
        clean_button.config(state="normal" if selected_file else "disabled")
        choose_button.config(state="normal")


# =========================
# UI components
# =========================
def create_stat_card(parent, title, initial_value, accent, subtitle):
    card = tk.Frame(
        parent,
        bg=PANEL,
        highlightbackground=BORDER,
        highlightthickness=1,
        padx=16,
        pady=14,
    )
    tk.Frame(card, bg=accent, height=4).pack(fill="x")
    tk.Label(
        card,
        text=title.upper(),
        font=("Segoe UI", 8, "bold"),
        bg=PANEL,
        fg=MUTED,
    ).pack(anchor="w", pady=(11, 5))
    value = tk.Label(
        card,
        text=initial_value,
        font=("Segoe UI", 23, "bold"),
        bg=PANEL,
        fg=accent,
    )
    value.pack(anchor="w")
    tk.Label(
        card,
        text=subtitle,
        font=("Segoe UI", 8),
        bg=PANEL,
        fg=MUTED,
    ).pack(anchor="w", pady=(4, 0))
    return card, value


# =========================
# Main window
# =========================
root = tk.Tk()
root.title("Data Cleaning Tool | Data Quality Workspace")
root.geometry("1060x850")
root.minsize(800, 720)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Primary.TButton",
    font=("Segoe UI", 10, "bold"),
    padding=(16, 10),
    background=BLUE,
    foreground=WHITE,
    borderwidth=0,
)
style.map(
    "Primary.TButton",
    background=[("active", BLUE_HOVER), ("disabled", "#A8B8D8")],
    foreground=[("disabled", "#F7F9FC")],
)
style.configure(
    "Secondary.TButton",
    font=("Segoe UI", 9, "bold"),
    padding=(12, 9),
    background="#E8EEF8",
    foreground=NAVY,
    borderwidth=0,
)
style.map(
    "Secondary.TButton",
    background=[("active", "#D9E4F5"), ("disabled", "#EDF1F7")],
)
style.configure(
    "Horizontal.TProgressbar",
    troughcolor="#DCE5F0",
    background=BLUE,
    thickness=7,
)

# Header
header = tk.Frame(root, bg=NAVY, padx=28, pady=23)
header.pack(fill="x")
header_top = tk.Frame(header, bg=NAVY)
header_top.pack(fill="x")

brand = tk.Frame(header_top, bg=NAVY)
brand.pack(side="left", fill="x", expand=True)

tk.Label(
    brand,
    text="DATA QUALITY WORKSPACE",
    font=("Segoe UI", 21, "bold"),
    bg=NAVY,
    fg=WHITE,
).pack(anchor="w")
tk.Label(
    brand,
    text="Clean, standardize, and prepare your data for analysis.",
    font=("Segoe UI", 10),
    bg=NAVY,
    fg="#D5E2F4",
).pack(anchor="w", pady=(5, 0))

tk.Label(
    header_top,
    text="PYTHON  •  PANDAS",
    font=("Segoe UI", 9, "bold"),
    bg=NAVY_LIGHT,
    fg="#FFFFFF",
    padx=13,
    pady=8,
).pack(side="right", anchor="n")

# Main area
main = tk.Frame(root, bg=BG, padx=26, pady=22)
main.pack(fill="both", expand=True)

tk.Label(
    main,
    text="Start a cleaning session",
    font=("Segoe UI", 15, "bold"),
    bg=BG,
    fg=TEXT,
).pack(anchor="w")
tk.Label(
    main,
    text="Choose a CSV or Excel file. Your original file will not be overwritten.",
    font=("Segoe UI", 9),
    bg=BG,
    fg=MUTED,
).pack(anchor="w", pady=(3, 13))

# File panel
file_panel = tk.Frame(
    main,
    bg=PANEL,
    padx=18,
    pady=16,
    highlightbackground=BORDER,
    highlightthickness=1,
)
file_panel.pack(fill="x", pady=(0, 15))

file_header = tk.Frame(file_panel, bg=PANEL)
file_header.pack(fill="x")
tk.Label(
    file_header,
    text="1   INPUT FILE",
    font=("Segoe UI", 10, "bold"),
    bg=PANEL,
    fg=NAVY,
).pack(side="left")
tk.Label(
    file_header,
    text="SUPPORTED: .CSV  /  .XLSX",
    font=("Segoe UI", 8, "bold"),
    bg=PALE_BLUE,
    fg=BLUE,
    padx=9,
    pady=5,
).pack(side="right")

file_name_label = tk.Label(
    file_panel,
    text="No file selected",
    font=("Segoe UI", 11, "bold"),
    bg=PANEL,
    fg=TEXT,
    anchor="w",
)
file_name_label.pack(fill="x", pady=(13, 3))
file_path_label = tk.Label(
    file_panel,
    text="Select a file from your computer to begin.",
    font=("Segoe UI", 9),
    bg=PANEL,
    fg=MUTED,
    anchor="w",
    wraplength=900,
    justify="left",
)
file_path_label.pack(fill="x", pady=(0, 13))

file_actions = tk.Frame(file_panel, bg=PANEL)
file_actions.pack(fill="x")
choose_button = ttk.Button(
    file_actions,
    text="Choose data file",
    style="Primary.TButton",
    command=choose_file,
)
choose_button.pack(side="left")
clean_button = ttk.Button(
    file_actions,
    text="Clean data",
    style="Secondary.TButton",
    command=clean_data,
    state="disabled",
)
clean_button.pack(side="left", padx=(9, 0))

# Status and progress
status_row = tk.Frame(main, bg=BG)
status_row.pack(fill="x", pady=(0, 7))
tk.Label(
    status_row,
    text="STATUS",
    font=("Segoe UI", 8, "bold"),
    bg=BG,
    fg=MUTED,
).pack(side="left")
status_label = tk.Label(
    status_row,
    text="Choose a file to get started.",
    font=("Segoe UI", 9, "bold"),
    bg=BG,
    fg=MUTED,
)
status_label.pack(side="left", padx=(9, 0))

progress_bar = ttk.Progressbar(main, mode="indeterminate")
progress_bar.pack(fill="x", pady=(0, 17))

# Statistics
stats_heading = tk.Frame(main, bg=BG)
stats_heading.pack(fill="x", pady=(0, 10))
tk.Label(
    stats_heading,
    text="2   DATA QUALITY OVERVIEW",
    font=("Segoe UI", 11, "bold"),
    bg=BG,
    fg=NAVY,
).pack(side="left")
tk.Label(
    stats_heading,
    text="Updates after cleaning",
    font=("Segoe UI", 8),
    bg=BG,
    fg=MUTED,
).pack(side="right")

cards_frame = tk.Frame(main, bg=BG)
cards_frame.pack(fill="x", pady=(0, 17))

card_specs = [
    ("Original rows", "—", BLUE, "Rows in source file"),
    ("Final rows", "—", GREEN, "Rows after cleaning"),
    ("Duplicates removed", "—", ORANGE, "Exact duplicate rows"),
    ("Missing cells", "—", RED, "Empty cells found"),
]
card_values = []
for index, (title, initial, accent, subtitle) in enumerate(card_specs):
    card, value = create_stat_card(cards_frame, title, initial, accent, subtitle)
    card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 6, 0))
    cards_frame.columnconfigure(index, weight=1, uniform="stat")
    card_values.append(value)

rows_before_value, rows_after_value, duplicates_value, missing_value = card_values

# Results panel
results_panel = tk.Frame(
    main,
    bg=PANEL,
    padx=17,
    pady=14,
    highlightbackground=BORDER,
    highlightthickness=1,
)
results_panel.pack(fill="both", expand=True)

results_header = tk.Frame(results_panel, bg=PANEL)
results_header.pack(fill="x", pady=(0, 9))
tk.Label(
    results_header,
    text="3   CLEANING SUMMARY",
    font=("Segoe UI", 11, "bold"),
    bg=PANEL,
    fg=NAVY,
).pack(side="left")
tk.Label(
    results_header,
    text="Detailed report",
    font=("Segoe UI", 8),
    bg=PANEL,
    fg=MUTED,
).pack(side="right")

results_box = tk.Text(
    results_panel,
    height=9,
    wrap="word",
    font=("Consolas", 9),
    bg="#F8FAFD",
    fg=TEXT,
    padx=13,
    pady=12,
    relief="flat",
    borderwidth=0,
    insertbackground=TEXT,
)
results_box.pack(fill="both", expand=True)
results_box.insert(
    tk.END,
    "Your cleaning summary will appear here after you process a file.\n\n"
    "The tool can trim extra spaces, standardize dates, clean basic Egyptian "
    "mobile phone formatting, remove exact duplicate rows, and report missing values.",
)
results_box.config(state="disabled")

# Output actions
output_actions = tk.Frame(main, bg=BG)
output_actions.pack(fill="x", pady=(13, 0))

open_file_button = ttk.Button(
    output_actions,
    text="Open cleaned file",
    style="Secondary.TButton",
    command=lambda: open_file(output_file),
    state="disabled",
)
open_file_button.pack(side="left")

open_report_button = ttk.Button(
    output_actions,
    text="Open report",
    style="Secondary.TButton",
    command=lambda: open_file(report_file),
    state="disabled",
)
open_report_button.pack(side="left", padx=(8, 0))

open_folder_button = ttk.Button(
    output_actions,
    text="Open output folder",
    style="Secondary.TButton",
    command=lambda: open_output_folder(output_file),
    state="disabled",
)
open_folder_button.pack(side="left", padx=(8, 0))

# Footer
footer = tk.Frame(root, bg="#E8EEF6", padx=26, pady=10)
footer.pack(fill="x")
tk.Label(
    footer,
    text="DATA CLEANING TOOL",
    font=("Segoe UI", 8, "bold"),
    bg="#E8EEF6",
    fg=NAVY,
).pack(side="left")
tk.Label(
    footer,
    text="Built with Python • Pandas • Tkinter",
    font=("Segoe UI", 8),
    bg="#E8EEF6",
    fg=MUTED,
).pack(side="right")

root.mainloop()

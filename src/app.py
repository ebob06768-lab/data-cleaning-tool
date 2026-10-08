
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import pandas as pd

# =========================
# Project settings
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"

selected_file = None
output_file = None
report_file = None

BG = "#F4F7FB"
NAVY = "#183153"
BLUE = "#2864DC"
GREEN = "#16845B"
ORANGE = "#C47A13"
RED = "#C34242"
WHITE = "#FFFFFF"
MUTED = "#64748B"


# =========================
# Helper functions
# =========================

def open_file(path):
    if path and Path(path).exists():
        try:
            os.startfile(str(path))
        except OSError as error:
            messagebox.showerror("Open Error", str(error))
    else:
        messagebox.showwarning(
            "File not found",
            "The file has not been created yet."
        )


def open_folder(path):
    if path and Path(path).exists():
        try:
            os.startfile(str(Path(path).parent))
        except OSError as error:
            messagebox.showerror("Open Error", str(error))


def update_card(label, value):
    label.config(text=str(value))


# =========================
# Choose input file
# =========================

def choose_file():
    global selected_file

    filename = filedialog.askopenfilename(
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

    status_label.config(
        text="File selected — ready to clean",
        fg=GREEN,
    )

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
        )
        return

    clean_button.config(state="disabled")
    status_label.config(text="Cleaning data...", fg=ORANGE)
    progress_bar.start(10)
    root.update_idletasks()

    try:
        # Read input
        if selected_file.suffix.lower() == ".csv":
            df = pd.read_csv(
                selected_file,
                dtype={"Phone": "string"},
            )
        elif selected_file.suffix.lower() == ".xlsx":
            df = pd.read_excel(
                selected_file,
                dtype={"Phone": "string"},
            )
        else:
            raise ValueError("Only CSV and XLSX files are supported.")

        rows_before = len(df)
        total_cells = df.shape[0] * df.shape[1]

        # Record missing values before cleaning
        missing_report = {
            column: int(count)
            for column, count in df.isnull().sum().items()
            if count > 0
        }

        missing_cells = sum(missing_report.values())

        missing_percentage = (
            missing_cells / total_cells * 100
            if total_cells
            else 0
        )

        # Trim text spaces
        spaces_cleaned = 0

        for column in df.columns:
            if (
                pd.api.types.is_object_dtype(df[column].dtype)
                or isinstance(df[column].dtype, pd.StringDtype)
            ):
                def trim_value(value):
                    if isinstance(value, str):
                        return value.strip()
                    return value

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

        # Standardize dates
        if "Date" in df.columns:
            dates = pd.to_datetime(
                df["Date"],
                format="mixed",
                dayfirst=True,
                errors="coerce",
            )
            df["Date"] = dates.dt.strftime("%Y-%m-%d")

        # Clean phone numbers
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

        # Remove exact duplicate rows
        df = df.drop_duplicates()

        rows_after = len(df)
        duplicates_removed = rows_before - rows_after

        # Save cleaned file
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        output_file = DATA_DIR / (
            f"{selected_file.stem}_cleaned{selected_file.suffix}"
        )

        if selected_file.suffix.lower() == ".xlsx":
            df.to_excel(output_file, index=False)
        else:
            df.to_csv(
                output_file,
                index=False,
                encoding="utf-8-sig",
            )

        # Write report
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
            report.write(
                f"Duplicates removed: {duplicates_removed}\n"
            )
            report.write(f"Spaces cleaned: {spaces_cleaned}\n")
            report.write(
                f"Missing cells: {missing_cells} "
                f"({missing_percentage:.2f}%)\n\n"
            )
            report.write("Missing values by column:\n")

            if missing_report:
                for column, count in missing_report.items():
                    percentage = (
                        count / rows_before * 100
                        if rows_before
                        else 0
                    )
                    report.write(
                        f"- {column}: {count} "
                        f"({percentage:.2f}% of rows)\n"
                    )
            else:
                report.write("- None\n")

        # Update statistic cards
        update_card(rows_before_value, rows_before)
        update_card(rows_after_value, rows_after)
        update_card(duplicates_value, duplicates_removed)
        update_card(missing_value, f"{missing_percentage:.1f}%")

        # Update results panel
        results_box.config(state="normal")
        results_box.delete("1.0", tk.END)

        results_box.insert(
            tk.END,
            "CLEANING COMPLETED SUCCESSFULLY\n"
            "================================\n\n"
            f"Input file: {selected_file.name}\n"
            f"Original rows: {rows_before}\n"
            f"Final rows: {rows_after}\n"
            f"Duplicates removed: {duplicates_removed}\n"
            f"Spaces cleaned: {spaces_cleaned}\n"
            f"Missing cells: {missing_cells}\n\n"
            "MISSING VALUES BY COLUMN\n"
            "------------------------\n"
        )

        if missing_report:
            for column, count in missing_report.items():
                percentage = (
                    count / rows_before * 100
                    if rows_before
                    else 0
                )
                results_box.insert(
                    tk.END,
                    f"{column}: {count} ({percentage:.2f}%)\n",
                )
        else:
            results_box.insert(tk.END, "No missing values found.\n")

        results_box.insert(
            tk.END,
            f"\nCleaned file:\n{output_file}\n"
            f"\nReport:\n{report_file}\n",
        )

        results_box.config(state="disabled")

        open_file_button.config(state="normal")
        open_report_button.config(state="normal")

        status_label.config(
            text="Cleaning completed successfully!",
            fg=GREEN,
        )

        messagebox.showinfo(
            "Success",
            "Your data has been cleaned successfully!",
        )

    except Exception as error:
        status_label.config(text="Cleaning failed.", fg=RED)

        messagebox.showerror(
            "Cleaning Error",
            f"An error occurred:\n\n{error}",
        )

    finally:
        progress_bar.stop()
        clean_button.config(state="normal")


# =========================
# Build interface
# =========================

root = tk.Tk()
root.title("Data Cleaning Tool")
root.geometry("900x790")
root.minsize(700, 650)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")

style.configure(
    "Main.TButton",
    font=("Segoe UI", 10, "bold"),
    padding=9,
)

style.configure(
    "Horizontal.TProgressbar",
    troughcolor="#DCE5F0",
    background=BLUE,
)

# Header
header = tk.Frame(root, bg=NAVY, padx=25, pady=20)
header.pack(fill="x")

tk.Label(
    header,
    text="DATA CLEANING TOOL",
    font=("Segoe UI", 22, "bold"),
    bg=NAVY,
    fg=WHITE,
).pack(anchor="w")

tk.Label(
    header,
    text="A simple workspace for cleaner, better-quality data",
    font=("Segoe UI", 10),
    bg=NAVY,
    fg="#D9E5F5",
).pack(anchor="w", pady=(5, 0))

# Main content
main = tk.Frame(root, bg=BG, padx=24, pady=18)
main.pack(fill="both", expand=True)

# File selection panel
file_panel = tk.Frame(
    main,
    bg=WHITE,
    padx=16,
    pady=14,
    highlightbackground="#DCE4EF",
    highlightthickness=1,
)
file_panel.pack(fill="x", pady=(0, 15))

tk.Label(
    file_panel,
    text="INPUT FILE",
    font=("Segoe UI", 10, "bold"),
    bg=WHITE,
    fg=NAVY,
).pack(anchor="w")

file_name_label = tk.Label(
    file_panel,
    text="No file selected",
    font=("Segoe UI", 11, "bold"),
    bg=WHITE,
    fg="#334155",
    anchor="w",
)
file_name_label.pack(fill="x", pady=(8, 2))

file_path_label = tk.Label(
    file_panel,
    text="Choose a CSV or Excel file to begin.",
    font=("Segoe UI", 9),
    bg=WHITE,
    fg=MUTED,
    anchor="w",
    wraplength=790,
)
file_path_label.pack(fill="x", pady=(0, 10))

ttk.Button(
    file_panel,
    text="Choose File",
    style="Main.TButton",
    command=choose_file,
).pack(anchor="w")

# Action buttons
actions = tk.Frame(main, bg=BG)
actions.pack(fill="x", pady=(0, 12))

clean_button = ttk.Button(
    actions,
    text="Clean Data",
    style="Main.TButton",
    command=clean_data,
    state="disabled",
)
clean_button.pack(side="left", padx=(0, 8))

open_file_button = ttk.Button(
    actions,
    text="Open Cleaned File",
    command=lambda: open_file(output_file),
    state="disabled",
)
open_file_button.pack(side="left", padx=(0, 8))

open_report_button = ttk.Button(
    actions,
    text="Open Report",
    command=lambda: open_file(report_file),
    state="disabled",
)
open_report_button.pack(side="left")

# Status and progress
status_label = tk.Label(
    main,
    text="Choose a file to get started.",
    font=("Segoe UI", 10, "bold"),
    bg=BG,
    fg=MUTED,
    anchor="w",
)
status_label.pack(fill="x", pady=(0, 7))

progress_bar = ttk.Progressbar(
    main,
    mode="indeterminate",
    style="Horizontal.TProgressbar",
)
progress_bar.pack(fill="x", pady=(0, 16))

# Statistics heading
tk.Label(
    main,
    text="DATA QUALITY OVERVIEW",
    font=("Segoe UI", 12, "bold"),
    bg=BG,
    fg=NAVY,
).pack(anchor="w", pady=(0, 10))

# Statistic cards
cards_frame = tk.Frame(main, bg=BG)
cards_frame.pack(fill="x", pady=(0, 16))

def create_card(parent, title, initial_value, accent):
    card = tk.Frame(
        parent,
        bg=WHITE,
        padx=12,
        pady=13,
        highlightbackground="#DCE4EF",
        highlightthickness=1,
    )

    tk.Frame(card, bg=accent, height=4).pack(fill="x")

    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 9),
        bg=WHITE,
        fg=MUTED,
    ).pack(anchor="w", pady=(10, 5))

    value_label = tk.Label(
        card,
        text=initial_value,
        font=("Segoe UI", 22, "bold"),
        bg=WHITE,
        fg=accent,
    )
    value_label.pack(anchor="w")

    return card, value_label


card_specs = [
    ("Original Rows", "—", BLUE),
    ("Final Rows", "—", GREEN),
    ("Duplicates Removed", "—", ORANGE),
    ("Missing Cells", "—", RED),
]

card_values = []

for index, (title, initial, color) in enumerate(card_specs):
    card, value_label = create_card(
        cards_frame,
        title,
        initial,
        color,
    )
    card.grid(
        row=0,
        column=index,
        sticky="nsew",
        padx=4,
    )
    card_values.append(value_label)

for index in range(4):
    cards_frame.columnconfigure(index, weight=1)

(
    rows_before_value,
    rows_after_value,
    duplicates_value,
    missing_value,
) = card_values

# Results
tk.Label(
    main,
    text="CLEANING DETAILS",
    font=("Segoe UI", 12, "bold"),
    bg=BG,
    fg=NAVY,
).pack(anchor="w", pady=(0, 8))

results_box = tk.Text(
    main,
    height=10,
    wrap="word",
    font=("Consolas", 9),
    bg=WHITE,
    fg="#263445",
    padx=12,
    pady=10,
    relief="solid",
    borderwidth=1,
)
results_box.pack(fill="both", expand=True)
results_box.insert(
    tk.END,
    "Your cleaning summary will appear here after processing a file.",
)
results_box.config(state="disabled")

# Footer
tk.Label(
    root,
    text="Python • Pandas • Tkinter",
    font=("Segoe UI", 9),
    bg=BG,
    fg=MUTED,
    pady=9,
).pack()

root.mainloop()

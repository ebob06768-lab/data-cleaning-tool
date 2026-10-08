import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog

# =========================
# 1. تحديد مسارات المشروع
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

data_dir = BASE_DIR / "data"
reports_dir = BASE_DIR / "reports"

csv_file = data_dir / "raw_data.csv"
excel_file = data_dir / "raw_data.xlsx"

output_file = data_dir / "cleaned_data.csv"
report_file = reports_dir / "cleaning_report.txt"


# =========================# =========================
# اختيار ملف من الكمبيوتر
# =========================

root = tk.Tk()
root.withdraw()

input_file = filedialog.askopenfilename(
    title="Choose CSV or Excel file",
    filetypes=[
        ("CSV files", "*.csv"),
        ("Excel files", "*.xlsx")
    ]
)

if not input_file:
    raise SystemExit("لم يتم اختيار أي ملف.")

input_file = Path(input_file)

print(f"Input file: {input_file.name}")
# =========================
# 3. قراءة البيانات
# =========================

if input_file.suffix.lower() == ".csv":

    df = pd.read_csv(
        input_file,
        skipinitialspace=False,
        dtype={"Phone": str}
    )

elif input_file.suffix.lower() == ".xlsx":

    df = pd.read_excel(
        input_file,
        dtype={"Phone": "string"}
    )

    

else:

    raise ValueError(
        "نوع الملف غير مدعوم. استخدم CSV أو XLSX."
    )


# =========================
# 4. معلومات قبل التنظيف
# =========================

rows_before = len(df)


# =========================
# 5. اكتشاف القيم الناقصة
# =========================

missing_values = df.isnull().sum()

missing_report = {}

for column, count in missing_values.items():

    if count > 0:

        missing_percentage = (
            count / len(df) * 100
            if len(df) > 0
            else 0
        )

        missing_report[column] = {
            "count": int(count),
            "percentage": round(missing_percentage, 2)
        }


# =========================
# 6. تنظيف المسافات
# =========================

spaces_cleaned = 0

for column in df.select_dtypes(include="str").columns:

    before = df[column].copy()

    df[column] = df[column].str.strip()

    spaces_cleaned += (
        before.fillna("").str.len()
        - df[column].fillna("").str.len()
    ).sum()


# =========================
# 7. توحيد التاريخ
# =========================

if "Date" in df.columns:

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )

    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")


# =========================
# 8. تنظيف رقم الهاتف
# =========================

if "Phone" in df.columns:

    df["Phone"] = df["Phone"].astype("string").str.strip()

    # إزالة المسافات والشرطات
    df["Phone"] = df["Phone"].str.replace(
        r"[\s\-]+",
        "",
        regex=True
    )

    # إضافة الصفر للأرقام المصرية التي فقدت الصفر الأول
    df["Phone"] = df["Phone"].apply(
        lambda phone: (
            "0" + phone
            if pd.notna(phone)
            and phone.isdigit()
            and len(phone) == 10
            and phone.startswith(("10", "11", "12", "15"))
            else phone
        )
    )


# =========================
# 9. حذف التكرارات
# =========================

df = df.drop_duplicates()

rows_after = len(df)

duplicates_removed = rows_before - rows_after


# =========================
# 10. حفظ الملف النظيف
# =========================

output_file = data_dir / f"{input_file.stem}_cleaned{input_file.suffix}"

if input_file.suffix.lower() == ".xlsx":

    df.to_excel(output_file, index=False)

else:

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

# =========================
# 11. إنشاء التقرير
# =========================

reports_dir.mkdir(parents=True, exist_ok=True)

report_file = reports_dir / f"{input_file.stem}_cleaning_report.txt"

with open(report_file, "w", encoding="utf-8") as report:

    report.write("DATA CLEANING REPORT\n")
    report.write("====================\n\n")

    report.write(f"Input file: {input_file.name}\n")
    report.write(f"Output file: {output_file.name}\n")
    report.write(f"Original rows: {rows_before}\n")
    report.write(f"Final rows: {rows_after}\n")
    report.write(f"Duplicates removed: {duplicates_removed}\n")
    report.write(f"Spaces cleaned: {int(spaces_cleaned)}\n\n")

    report.write("Missing values before cleaning:\n")

    if missing_report:

        for column, details in missing_report.items():

            report.write(
                f"- {column}: {details['count']} missing "
                f"({details['percentage']}%)\n"
            )

    else:

        report.write("- None\n")

    report.write("\nDate column standardized to YYYY-MM-DD\n")

# =========================
# 12. عرض النتيجة
# =========================

print("\n=== CLEANING COMPLETED ===")

print(f"Original rows: {rows_before}")
print(f"Final rows: {rows_after}")
print(f"Duplicates removed: {duplicates_removed}")
print(f"Spaces cleaned: {int(spaces_cleaned)}")

print("\nMissing values:")

if missing_report:

    for column, details in missing_report.items():

        print(
            f"- {column}: {details['count']} missing "
            f"({details['percentage']}%)"
        )

else:

    print("- None")


print("\nCleaned file:")
print(output_file)

print("\nReport:")
print(report_file)
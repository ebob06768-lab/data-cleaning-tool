# 🧹 Data Cleaning Tool

A Python desktop application for cleaning and preparing CSV and Excel files for data analysis.

## 📌 Overview

**Data Cleaning Tool** is a desktop application built with Python that helps users clean and prepare raw datasets before using them for analysis or visualization.

The application provides a simple graphical interface that allows users to select CSV or Excel files, clean common data-quality issues, and generate a cleaning report.

## ✨ Features

- 📂 Import CSV and Excel files
- 🧹 Remove duplicate rows
- ✂️ Clean unnecessary spaces
- 📅 Standardize date formats
- 📱 Clean and standardize Egyptian mobile phone numbers
- 🔎 Detect missing values
- 📊 Display cleaning statistics
- 📈 Show original and final row counts
- 📝 Generate a detailed cleaning report
- 💾 Export cleaned datasets
- 🖥️ Simple Tkinter graphical interface
- 📊 Support for Excel and CSV files

## 🛠️ Technologies Used

- **Python 3**
- **Pandas**
- **Tkinter**
- **OpenPyXL**
- **CSV**
- **Excel**

## 📁 Project Structure

```text
data-cleaning-tool/
│
├── data/
│   ├── raw_data.csv
│   ├── raw_data.xlsx
│   └── raw_data_cleaned.xlsx
│
├── reports/
│   └── raw_data_cleaning_report.txt
│
├── src/
│   ├── cleaner.py
│   └── app.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/data-cleaning-tool.git
```

Open the project folder:

```bash
cd data-cleaning-tool
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

## ▶️ Run the Application

Run the graphical interface:

```bash
python src/app.py
```

The application will open a desktop window where you can select a CSV or Excel file and start cleaning the data.

## 📊 Example

The application can handle common data-quality problems such as:

**Before cleaning:**

```text
 Ahmed , ahmed@gmail.com ,01012345678,01/05/2026
Ahmed,ahmed@gmail.com,01012345678,2026-05-01
```

**After cleaning:**

```text
Ahmed,ahmed@gmail.com,01012345678,2026-05-01
```

The application also reports:

- Number of original rows
- Number of final rows
- Number of duplicates removed
- Missing values
- Number of cleaned spaces

## 🎯 Project Goal

The goal of this project is to demonstrate practical skills in:

- Data cleaning
- Data preprocessing
- Python programming
- Pandas
- GUI development
- Working with CSV and Excel datasets
- Generating data-quality reports

## 🔮 Future Improvements

Possible future improvements include:

- Data visualization dashboard
- More advanced data validation
- Support for larger datasets
- Automatic detection of incorrect data types
- Export cleaning reports as PDF
- Drag-and-drop file support
- More advanced phone and email validation

## 👨‍💻 Author

**Ehab Abdullah**

Information Systems Student  
Assiut University

---

⭐ If you find this project useful, feel free to star the repository.
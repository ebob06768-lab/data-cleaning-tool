# Data Cleaning Tool

A Python desktop application for cleaning CSV and Excel datasets using Pandas and Tkinter.

## Features

- Import CSV and Excel (`.xlsx`) files.
- Remove leading and trailing spaces from text values.
- Standardize dates to `YYYY-MM-DD`.
- Remove duplicate rows.
- Detect missing values and calculate percentages.
- Clean phone number formatting.
- Export cleaned files while preserving the input file type.
- Generate a text report summarizing the cleaning process.
- View cleaning statistics in a graphical interface.
- Open the cleaned file and report directly from the application.

## Technologies

- Python
- Pandas
- Tkinter
- OpenPyXL

## Project Structure

```text
data-cleaning-tool/
├── data/
├── reports/
├── src/
│   ├── app.py
│   └── cleaner.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Installation

1. Install Python 3.
2. Clone or download this repository.
3. Open a terminal in the project directory.
4. Install the required packages:

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
python src/app.py
```

## How to Use

1. Launch the application.
2. Choose a CSV or Excel file.
3. Click **Clean Data**.
4. Review the cleaning statistics.
5. Open the cleaned dataset or cleaning report.

## Output

The application creates a cleaned copy of the input file in the `data/` directory and a cleaning report in the `reports/` directory.

The original input file is not intentionally overwritten.

## Limitations

- Date parsing can be ambiguous when day and month values are both 12 or lower.
- Phone number normalization assumes certain Egyptian mobile number formats.
- Missing values are reported, not automatically filled.
- Excel formatting and formulas may not be preserved when exporting the cleaned dataset.

## Future Improvements

- Data validation and configurable cleaning rules.
- Automated tests.
- Support for additional file formats.
- More detailed data quality metrics.
- Improved interface and progress feedback.

## Author

Created as a practical Python and data analytics portfolio project.
# EconoCausal: Dynamic Pricing via Double Machine Learning

**Team Group:** 22
**Organization:** Infotact Solutions Internship
**Assignment ID:** ITS/DSML/1192
**Domain:** Data Science & Machine Learning

## Project Overview

This repository is the shared workspace for the EconoCausal project. The project focuses on investigating dynamic pricing using Double Machine Learning (DML). The exact business question, dataset, target variables, and evaluation requirements must be confirmed with the assigned mentor before implementation.

## Team

- Hansika Gehlot — Team Leader
- Kumbha Siva Ganesh
- Duppada Dhanalakshmi
- Hassan Baig

## Planned Workflow

1. Confirm the problem statement, dataset, deliverables, and deadline.
2. Load and inspect the approved dataset (Online Retail II is the current
   provisional candidate; confirm the source and version before analysis).
3. Clean the data and perform exploratory data analysis (EDA).
4. Define the causal question, treatment, outcome, and confounders with mentor guidance.
5. Build a baseline and implement an appropriate DML approach.
6. Evaluate assumptions and results using suitable metrics and diagnostics.
7. Document findings and prepare the required report and final deliverables.

## Repository Structure

```text
EconoCausal-Team22/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── src/
│   ├── data/
│   ├── features/
│   ├── models/
│   └── evaluation/
├── reports/
│   └── figures/
├── presentation/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Recommended Python version: 3.10 or 3.11, subject to course requirements.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Preprocessing and EDA

The reusable workflow in `src/data/retail_eda.py` is designed around the
provisional Online Retail II transaction schema. Place the approved CSV or
Excel workbook in `data/raw/` (raw data is ignored by Git), then run from the
repository root:

```bash
python -m src.data.retail_eda data/raw/online_retail_II.xlsx
```

For CSV input, use the same command with the `.csv` file. Excel workbooks are
read across all sheets by default; select one sheet with `--sheet "2010-2011"`.
Use `--output-dir <path>` to change the default output directory
`data/processed/eda/`.

Before changing column names or types, the workflow records an initial
inspection for each source file or workbook sheet under
`data/processed/eda/initial_inspection/`. The inspection includes row/column
dimensions, original dtypes, deep memory usage, `DataFrame.info()`, the first
and last five rows, `describe(include="all")`, and a column-format audit for
whitespace, aliases, duplicate labels, and names that normalize to the same
identifier. The audit preserves original input labels so naming inconsistencies
remain visible even when a recognized alias is normalized for processing.

The workflow writes a normalized file retaining every input row and quality
flags, a separate `deduplicated_transactions.csv` file that drops exact
duplicate transaction rows while retaining the first occurrence, a positive-sales
analysis sample, an explicit row-selection audit, per-column null counts in
`missing_values.csv`, quality and missingness summaries, numeric/categorical
summaries, outlier-review bounds, descriptive figures, and a generated
`eda_report.md`.
It does not automatically remove unusual stock codes or statistical outliers.
Univariate figures include histograms and box plots for price, quantity, and
gross line value, plus count plots for the most common countries and stock
codes. Box-plot fliers and IQR summaries are review signals, not automatic
exclusion rules.
Relationship analysis includes a price-versus-quantity scatter plot and, when
at least two eligible rows are available, a Pearson correlation heatmap and
matrix for price, quantity, and gross line value. The generated
`eda_report.md` summarizes observed quality flags, sample distributions,
correlations, and IQR outlier counts from the supplied data. Correlation findings
are descriptive, not causal; gross line value is mechanically computed from
price and quantity.
The report also highlights observed missing-value rates, sample retention,
outlier review bounds, and the most frequent country and stock code, with
reminders to review transaction flags and product scope.
Duplicates are determined across all transaction fields after normalization,
excluding only the workbook-sheet tracking field; the normalized audit file
retains duplicate rows and flags later occurrences for traceability.
Cancellation and return exclusions are clearly reported and must be reviewed
against the approved research question. Gross line value (`Quantity × Price`)
is descriptive only; it is not net revenue. EDA outputs do not by themselves
justify causal claims about price and quantity.

For missing data, all source rows and columns are preserved in the normalized
output. Rows missing required transaction fields (invoice, stock code, quantity,
invoice date, or price) are excluded from the analysis sample; missing optional
descriptions, customer IDs, and countries are retained. The workflow does not
automatically impute values or drop columns. This avoids inventing treatment,
outcome, identity, or date values; any imputation for later covariates should be
justified from the observed missingness pattern and documented before causal
analysis.

Run the focused tests with:

```bash
python -m pytest tests/test_retail_eda.py
```

### Interactive Streamlit dashboard

Launch the interactive dashboard from the repository root:

```bash
streamlit run src/data/retail_eda_app.py
```

Use the sidebar navigation to move between **Home / Dataset Upload**, **Data
Overview & Summary**, **Data Preprocessing (Cleaning & Transformation)**,
**Exploratory Data Analysis (Visualizations)**, and **Export Cleaned Data**.
Upload CSV, Excel, or JSON data; Excel workbooks can be analyzed one sheet at a
time or combined. The overview reports dimensions, dtypes, memory, missing and
duplicate row counts, and first/last row previews. Retail transaction files
matching the Online Retail II schema also use the existing retail-specific
quality audit; other tabular files use general-purpose inspection and
preprocessing.

Preprocessing options include dropping rows or columns with missing values,
imputing numerical data (mean, median, mode, or a chosen constant) and
categorical data (mode or a chosen constant), duplicate removal, IQR outlier
capping or Z-score filtering, one-hot or label encoding, and StandardScaler or
MinMaxScaler feature scaling. Choose target columns explicitly and apply the
steps to a working copy; the resulting cleaned data can be downloaded separately
from the unmodified normalized input. Numeric imputation offers mean, median,
mode, or constant; categorical imputation offers mode or constant (the
statistically meaningful choices for non-numeric categories). EDA charts update
with the sidebar filters and include selectable histograms, boxplots, category
count plots, scatterplots with linear trend lines, grouped bar analysis, and an
interactive Pearson correlation heatmap. Automated descriptive insights report
numeric distributions and feature pairs meeting the selected correlation
threshold. The Export Cleaned Data page downloads the final applied
preprocessing result as CSV. Dashboard calculations run in memory; uploaded data
is not written to the repository.

## Collaboration Rules

- Create a separate branch for each task, such as `feature/eda` or `feature/data-cleaning`.
- Open a Pull Request for review instead of pushing directly to `main`.
- Use clear commit messages, such as `Add initial EDA notebook`.
- Never commit passwords, API keys, personal data, or private datasets.
- Document dataset sources and applicable licenses.
- Do not claim results until experiments have been completed and verified.

## Project Status

Initial repository scaffold. Dataset selection, methodology confirmation, implementation, and evaluation are pending.

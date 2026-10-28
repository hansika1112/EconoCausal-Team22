from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "raw" / "online_retail_II.xlsx"
REPORT_DIR = ROOT / "reports"
REPORT_FILE = REPORT_DIR / "eda_summary.json"

SHEETS = ["Year 2009-2010", "Year 2010-2011"]
EXPECTED_COLUMNS = [
    "Invoice", "StockCode", "Description", "Quantity",
    "InvoiceDate", "Price", "Customer ID", "Country"
]


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    sheet_reports = []
    total_rows = 0
    missing_counts = {column: 0 for column in EXPECTED_COLUMNS}
    total_duplicates = 0
    combined_frames = []
    total_cancellations = 0
    total_negative_quantity = 0
    total_zero_price = 0
    total_high_quantity = 0
    total_high_price = 0
    total_negative_price = 0
    quantity_min = None
    quantity_max = None
    price_min = None
    price_max = None
    countries = set()

    for sheet in SHEETS:
        print(f"Analyzing sheet: {sheet}")
        df = pd.read_excel(
            DATA_FILE,
            sheet_name=sheet,
            engine="openpyxl"
        )

        df.columns = [str(column).strip() for column in df.columns]

        missing_columns = set(EXPECTED_COLUMNS) - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"Missing expected columns in {sheet}: {sorted(missing_columns)}"
            )

        rows = len(df)
        total_rows += rows

        for column in EXPECTED_COLUMNS:
            missing_counts[column] += int(df[column].isna().sum())

        duplicates = int(df.duplicated().sum())
        combined_frames.append(df.copy())
        cancellations = int(
            df["Invoice"].astype("string").str.startswith("C", na=False).sum()
        )
        negative_quantity = int((df["Quantity"] < 0).sum())
        zero_price = int((df["Price"] == 0).sum())
        high_quantity = int((df["Quantity"] > 1000).sum())
        high_price = int((df["Price"] > 1000).sum())
        negative_price = int((df["Price"] < 0).sum())

        total_duplicates += duplicates
        total_cancellations += cancellations
        total_negative_quantity += negative_quantity
        total_zero_price += zero_price
        total_high_quantity += high_quantity
        total_high_price += high_price
        total_negative_price += negative_price

        q_min, q_max = df["Quantity"].min(), df["Quantity"].max()
        p_min, p_max = df["Price"].min(), df["Price"].max()

        quantity_min = q_min if quantity_min is None else min(quantity_min, q_min)
        quantity_max = q_max if quantity_max is None else max(quantity_max, q_max)
        price_min = p_min if price_min is None else min(price_min, p_min)
        price_max = p_max if price_max is None else max(price_max, p_max)

        countries.update(df["Country"].dropna().astype(str).unique())

        sheet_reports.append({
            "sheet": sheet,
            "data_rows": rows,
            "duplicate_rows": duplicates,
            "missing_values": {
                column: int(df[column].isna().sum())
                for column in EXPECTED_COLUMNS
            },
            "cancellation_invoice_rows": cancellations,
            "negative_quantity_rows": negative_quantity,
            "zero_price_rows": zero_price,
            "quantity_over_1000_rows": high_quantity,
            "price_over_1000_rows": high_price,
            "negative_price_rows": negative_price
        })

        del df

    combined_df = pd.concat(combined_frames, ignore_index=True)
    total_duplicates = int(combined_df.duplicated().sum())
    del combined_df, combined_frames

    result = {
        "dataset": DATA_FILE.name,
        "inspection_type": "Initial EDA; raw dataset not modified",
        "total_data_rows": total_rows,
        "columns": EXPECTED_COLUMNS,
        "missing_values": missing_counts,
        "exact_duplicate_rows": total_duplicates,
        "duplicate_counting_note": "Exact duplicates counted after combining both sheets.",
        "cancellation_invoice_rows": total_cancellations,
        "negative_quantity_rows": total_negative_quantity,
        "zero_price_rows": total_zero_price,
        "quantity_over_1000_rows": total_high_quantity,
        "price_over_1000_rows": total_high_price,
        "negative_price_rows": total_negative_price,
        "quantity_min": quantity_min,
        "quantity_max": quantity_max,
        "price_min": price_min,
        "price_max": price_max,
        "unique_country_count": len(countries),
        "sheet_details": sheet_reports,
        "cleaning_decisions": (
            "No rows deleted. Flag unusual observations for investigation "
            "before deciding on preprocessing."
        )
    }

    REPORT_FILE.write_text(json.dumps(result, indent=2, default=str))
    print("\nEDA complete.")
    print(f"Total data rows: {total_rows:,}")
    print(f"Exact duplicate rows: {total_duplicates:,}")
    print(f"Missing Customer ID: {missing_counts['Customer ID']:,}")
    print(f"Quantity > 1000: {total_high_quantity:,}")
    print(f"Report saved to: {REPORT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

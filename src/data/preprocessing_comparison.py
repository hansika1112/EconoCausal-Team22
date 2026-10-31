from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "raw" / "online_retail_II.xlsx"
OUTPUT_FILE = ROOT / "reports" / "preprocessing_comparison.json"

SHEETS = ["Year 2009-2010", "Year 2010-2011"]
COLUMNS = ["Invoice", "Quantity", "Price"]


def summarize(df):
    required_columns = ["Invoice", "Quantity", "Price"]
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    for column in ["Quantity", "Price"]:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise TypeError(f"{column} must contain numeric values")

        if df[column].isna().any():
            raise ValueError(f"{column} contains missing values")

    return {
        "rows": int(len(df)),
        "quantity_mean": float(df["Quantity"].mean()),
        "quantity_median": float(df["Quantity"].median()),
        "price_mean": float(df["Price"].mean()),
        "price_median": float(df["Price"].median()),
        "quantity_min": float(df["Quantity"].min()),
        "quantity_max": float(df["Quantity"].max()),
        "price_min": float(df["Price"].min()),
        "price_max": float(df["Price"].max()),
        "quantity_std": float(df["Quantity"].std()),
        "price_std": float(df["Price"].std()),
    }

def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    frames = []

    for sheet in SHEETS:
        print(f"Reading {sheet}...")
        df = pd.read_excel(
            DATA_FILE,
            sheet_name=sheet,
            usecols=COLUMNS,
            engine="openpyxl"
        )
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)
    del frames

    cancellation = (
        data["Invoice"]
        .astype("string")
        .str.startswith("C", na=False)
    )
    negative_quantity = data["Quantity"] < 0
    nonpositive_price = data["Price"] <= 0

    scenarios = {
        "original": data,
        "exclude_cancellation_invoices": data.loc[~cancellation],
        "exclude_negative_quantities": data.loc[~negative_quantity],
        "exclude_nonpositive_prices": data.loc[~nonpositive_price],
        "positive_quantity_and_price": data.loc[
            (data["Quantity"] > 0) & (data["Price"] > 0)
        ],
        "positive_non_cancellation_sales": data.loc[
            (~cancellation)
            & (data["Quantity"] > 0)
            & (data["Price"] > 0)
        ],
    }

    original_rows = len(data)
    results = {
        "dataset": DATA_FILE.name,
        "original_rows": original_rows,
        "note": (
            "Comparison scenarios only. "
            "The raw dataset has not been modified."
        ),
        "scenarios": {},
    }

    for name, subset in scenarios.items():
        stats = summarize(subset)
        stats["excluded_rows"] = original_rows - stats["rows"]
        stats["retained_percent"] = round(
            100 * stats["rows"] / original_rows, 2
        )
        results["scenarios"][name] = stats

        print(
            f"{name}: {stats['rows']:,} rows "
            f"({stats['retained_percent']}% retained)"
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    print(f"\nReport saved to: {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

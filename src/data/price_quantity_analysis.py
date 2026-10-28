from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "raw" / "online_retail_II.xlsx"
REPORT_DIR = ROOT / "reports"
OUTPUT_FILE = REPORT_DIR / "price_quantity_summary.json"

SHEETS = ["Year 2009-2010", "Year 2010-2011"]
COLUMNS = ["Quantity", "Price"]


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
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

    results = {
        "dataset_rows": int(len(data)),
        "note": "Descriptive statistics only; no rows were deleted.",
        "columns": {}
    }

    for column in COLUMNS:
        values = pd.to_numeric(data[column], errors="coerce").dropna()
        results["columns"][column] = {
            "non_missing_count": int(values.count()),
            "minimum": float(values.min()),
            "p01": float(values.quantile(0.01)),
            "p05": float(values.quantile(0.05)),
            "p25": float(values.quantile(0.25)),
            "median": float(values.median()),
            "mean": float(values.mean()),
            "p75": float(values.quantile(0.75)),
            "p95": float(values.quantile(0.95)),
            "p99": float(values.quantile(0.99)),
            "maximum": float(values.max()),
            "standard_deviation": float(values.std()),
            "skewness": float(values.skew()),
            "zero_count": int((values == 0).sum()),
            "negative_count": int((values < 0).sum()),
            "positive_count": int((values > 0).sum())
        }

    OUTPUT_FILE.write_text(json.dumps(results, indent=2))
    print("\nDistribution analysis complete.")
    print(f"Rows analyzed: {len(data):,}")

    for column, stats in results["columns"].items():
        print(f"\n{column}")
        print(f"  Mean:   {stats['mean']:.4f}")
        print(f"  Median: {stats['median']:.4f}")
        print(f"  Min:    {stats['minimum']:.4f}")
        print(f"  Max:    {stats['maximum']:.4f}")
        print(f"  P01:    {stats['p01']:.4f}")
        print(f"  P99:    {stats['p99']:.4f}")
        print(f"  Skew:   {stats['skewness']:.4f}")

    print(f"\nReport saved to: {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

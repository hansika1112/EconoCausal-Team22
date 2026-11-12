from pathlib import Path
import json

from src.models.dml_estimator import run_pilot
from src.models.dml_diagnostics import build_diagnostics, save_diagnostics

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "processed" / "online_retail_clean.csv.gz"
OUTPUT_FILE = ROOT / "reports" / "dml_pilot_summary.json"


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    print("Loading data and preparing DML pilot...")

    result = run_pilot(
        csv_path=DATA_FILE,
        max_invoices=1500,
        n_splits=3,
        random_state=42,
    )

    print("\n========== DML PILOT DATA ==========")
    print(json.dumps(result["summary"], indent=2))

    diagnostics = build_diagnostics(result["estimator"])
    json_path, markdown_path = save_diagnostics(diagnostics, ROOT / "reports")

    print("\n========== DML DIAGNOSTICS ==========")
    print(json.dumps(diagnostics, indent=2))
    print(f"Diagnostic JSON: {json_path}")
    print(f"Diagnostic Markdown: {markdown_path}")

    print("\n========== TREATMENT EFFECT INFERENCE ==========")
    print(result["inference"].summary())

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(result["summary"], indent=2))

    print(f"\nPilot metadata saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

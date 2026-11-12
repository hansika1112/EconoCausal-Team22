from pathlib import Path
import json

from src.models.dml_estimator import run_pilot

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "processed" / "online_retail_clean.csv.gz"
OUTPUT_FILE = ROOT / "reports" / "dml_robustness.json"

SEEDS = [21, 42, 84]


def main():
    results = []

    for seed in SEEDS:
        print(f"\nRunning robustness sample: seed={seed}")

        result = run_pilot(
            csv_path=DATA_FILE,
            max_invoices=500,
            n_splits=3,
            random_state=seed,
        )

        inference = result["inference"]

        row = {
            "seed": seed,
            "rows": result["summary"]["rows"],
            "invoices": result["summary"]["invoices"],
            "estimate": float(inference.mean_point),
            "standard_error": float(inference.stderr_mean),
            "confidence_interval": [
                float(value)
                for value in inference.conf_int_mean()
            ],
        }

        results.append(row)
        print(row)

    report = {
        "method": "EconML LinearDML",
        "sample_invoices": 500,
        "cross_fitting_folds": 3,
        "seeds": SEEDS,
        "results": results,
        "interpretation": (
            "Preliminary sample-stability analysis. "
            "Observational estimates do not establish causality."
        ),
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(report, indent=2))

    print(f"\nRobustness report saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

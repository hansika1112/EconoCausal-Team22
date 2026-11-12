from pathlib import Path
import json

import numpy as np


def summarize_scores(scores, model_name):
    values = np.asarray(scores, dtype=float).ravel()

    if values.size == 0 or not np.isfinite(values).all():
        raise ValueError(f"Invalid diagnostic scores for {model_name}.")

    return {
        "model": model_name,
        "fold_scores": values.tolist(),
        "mean_r2": float(np.mean(values)),
        "std_r2": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
        "min_r2": float(np.min(values)),
        "max_r2": float(np.max(values)),
    }


def build_diagnostics(estimator):
    if not hasattr(estimator, "nuisance_scores_y"):
        raise AttributeError("Outcome nuisance scores are unavailable.")

    if not hasattr(estimator, "nuisance_scores_t"):
        raise AttributeError("Treatment nuisance scores are unavailable.")

    return {
        "outcome_model": summarize_scores(
            estimator.nuisance_scores_y,
            "log_quantity",
        ),
        "treatment_model": summarize_scores(
            estimator.nuisance_scores_t,
            "log_price",
        ),
        "interpretation": (
            "Nuisance-model R-squared scores are predictive diagnostics. "
            "They do not establish causal identification."
        ),
    }


def save_diagnostics(diagnostics, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "dml_diagnostics.json"
    markdown_path = output_dir / "dml_diagnostics.md"

    json_path.write_text(json.dumps(diagnostics, indent=2))

    lines = [
        "# DML Nuisance Model Diagnostics",
        "",
        "## Outcome Model",
        "",
        f"- Variable: {diagnostics['outcome_model']['model']}",
        f"- Fold scores: {diagnostics['outcome_model']['fold_scores']}",
        f"- Mean R²: {diagnostics['outcome_model']['mean_r2']:.4f}",
        f"- Standard deviation: {diagnostics['outcome_model']['std_r2']:.4f}",
        "",
        "## Treatment Model",
        "",
        f"- Variable: {diagnostics['treatment_model']['model']}",
        f"- Fold scores: {diagnostics['treatment_model']['fold_scores']}",
        f"- Mean R²: {diagnostics['treatment_model']['mean_r2']:.4f}",
        f"- Standard deviation: {diagnostics['treatment_model']['std_r2']:.4f}",
        "",
        "## Interpretation",
        "",
        diagnostics["interpretation"],
        "",
    ]

    markdown_path.write_text("\n".join(lines))

    return json_path, markdown_path

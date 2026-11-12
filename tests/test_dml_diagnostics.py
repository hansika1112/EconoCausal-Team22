import numpy as np
import pytest

from src.models.dml_diagnostics import (
    build_diagnostics,
    save_diagnostics,
    summarize_scores,
)


def test_summarize_scores():
    result = summarize_scores([0.2, 0.4, 0.6], "log_price")

    assert result["model"] == "log_price"
    assert result["mean_r2"] == pytest.approx(0.4)
    assert result["min_r2"] == pytest.approx(0.2)
    assert result["max_r2"] == pytest.approx(0.6)


def test_summarize_scores_rejects_empty_values():
    with pytest.raises(ValueError):
        summarize_scores([], "log_price")


def test_summarize_scores_rejects_nonfinite_values():
    with pytest.raises(ValueError):
        summarize_scores([0.2, np.nan], "log_price")


def test_build_diagnostics():
    class MockEstimator:
        nuisance_scores_y = [[0.1, 0.2, 0.3]]
        nuisance_scores_t = [[0.4, 0.5, 0.6]]

    result = build_diagnostics(MockEstimator())

    assert result["outcome_model"]["mean_r2"] == pytest.approx(0.2)
    assert result["treatment_model"]["mean_r2"] == pytest.approx(0.5)


def test_save_diagnostics(tmp_path):
    diagnostics = {
        "outcome_model": {
            "model": "log_quantity",
            "fold_scores": [0.1, 0.2],
            "mean_r2": 0.15,
            "std_r2": 0.0707,
            "min_r2": 0.1,
            "max_r2": 0.2,
        },
        "treatment_model": {
            "model": "log_price",
            "fold_scores": [0.3, 0.4],
            "mean_r2": 0.35,
            "std_r2": 0.0707,
            "min_r2": 0.3,
            "max_r2": 0.4,
        },
        "interpretation": "Predictive diagnostics only.",
    }

    json_path, markdown_path = save_diagnostics(
        diagnostics,
        tmp_path,
    )

    assert json_path.exists()
    assert markdown_path.exists()
    assert "DML Nuisance Model Diagnostics" in markdown_path.read_text()

import pandas as pd
import pytest

from src.models.feature_readiness import validate_dml_features


def test_valid_data_passes_readiness_checks():
    data = pd.DataFrame({
        "Price": [10.0, 12.0, 15.0],
        "Quantity": [5, 4, 3],
        "Country": ["UK", "UK", "France"],
    })

    result = validate_dml_features(
        data, treatment="Price", outcome="Quantity",
        confounders=["Country"],
    )

    assert result["ready"] is True
    assert result["row_count"] == 3
    assert result["complete_case_count"] == 3


def test_missing_required_column_raises_error():
    data = pd.DataFrame({"Price": [10.0], "Quantity": [2]})

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_dml_features(data, "Price", "Quantity", ["Country"])


def test_missing_values_are_reported():
    data = pd.DataFrame({
        "Price": [10.0, None],
        "Quantity": [5, 3],
    })

    result = validate_dml_features(data, "Price", "Quantity")

    assert result["ready"] is False
    assert result["missing_counts"]["Price"] == 1
    assert result["complete_case_count"] == 1


def test_non_numeric_treatment_is_rejected():
    data = pd.DataFrame({
        "Price": ["cheap", "expensive"],
        "Quantity": [5, 3],
    })

    with pytest.raises(TypeError, match="must be numeric"):
        validate_dml_features(data, "Price", "Quantity")


def test_treatment_and_outcome_must_differ():
    data = pd.DataFrame({"Price": [10.0]})

    with pytest.raises(ValueError, match="must be different"):
        validate_dml_features(data, "Price", "Price")


def test_nonpositive_treatment_and_outcome_are_flagged():
    data = pd.DataFrame({
        "Price": [10.0, 0.0, -5.0],
        "Quantity": [3, 0, 2],
    })

    result = validate_dml_features(data, "Price", "Quantity")

    assert result["ready"] is False
    assert result["invalid_nonpositive_counts"]["Price"] == 2
    assert result["invalid_nonpositive_counts"]["Quantity"] == 1

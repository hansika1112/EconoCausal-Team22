import pandas as pd
import pytest

from src.data.preprocessing_comparison import summarize


def test_summarize_returns_correct_row_count_and_statistics():
    df = pd.DataFrame({
        "Invoice": ["10001", "10002", "10003"],
        "Quantity": [2, 4, 6],
        "Price": [10.0, 20.0, 30.0],
    })

    result = summarize(df)

    assert result["rows"] == 3
    assert result["quantity_mean"] == 4.0
    assert result["quantity_median"] == 4.0
    assert result["price_mean"] == 20.0
    assert result["price_median"] == 20.0


def test_summarize_handles_single_row():
    df = pd.DataFrame({
        "Invoice": ["10001"],
        "Quantity": [5],
        "Price": [12.5],
    })

    result = summarize(df)

    assert result["rows"] == 1
    assert result["quantity_mean"] == 5.0
    assert result["quantity_median"] == 5.0
    assert result["price_mean"] == 12.5
    assert result["price_median"] == 12.5


def test_summarize_preserves_zero_and_negative_values():
    df = pd.DataFrame({
        "Invoice": ["10001", "10002", "10003"],
        "Quantity": [2, 0, -2],
        "Price": [10.0, 0.0, -10.0],
    })

    result = summarize(df)

    assert result["rows"] == 3
    assert result["quantity_mean"] == 0.0
    assert result["quantity_median"] == 0.0
    assert result["price_mean"] == 0.0
    assert result["price_median"] == 0.0


def test_summarize_handles_empty_dataframe():
    df = pd.DataFrame({
        "Invoice": pd.Series(dtype="string"),
        "Quantity": pd.Series(dtype="float64"),
        "Price": pd.Series(dtype="float64"),
    })

    result = summarize(df)

    assert result["rows"] == 0
    assert pd.isna(result["quantity_mean"])
    assert pd.isna(result["quantity_median"])
    assert pd.isna(result["price_mean"])
    assert pd.isna(result["price_median"])


def test_summarize_rejects_missing_required_columns():
    df = pd.DataFrame({
        "Invoice": ["10001"],
        "Quantity": [5],
    })

    with pytest.raises(KeyError):
        summarize(df)


def test_summarize_handles_fractional_values():
    df = pd.DataFrame({
        "Invoice": ["10001", "10002"],
        "Quantity": [1.5, 2.5],
        "Price": [10.25, 20.75],
    })

    result = summarize(df)

    assert result["rows"] == 2
    assert result["quantity_mean"] == 2.0
    assert result["quantity_median"] == 2.0
    assert result["price_mean"] == 15.5
    assert result["price_median"] == 15.5

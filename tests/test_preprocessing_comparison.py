import pandas as pd

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

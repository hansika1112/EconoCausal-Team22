import pandas as pd
import pytest

from src.data.eda_insights import generate_automated_insights


def test_automated_insights_summarize_distributions_and_high_correlations() -> None:
    frame = pd.DataFrame(
        {
            "units": [1, 2, 3, 4, 5],
            "revenue": [2, 4, 6, 8, 10],
            "category": ["a", "a", "b", "b", "b"],
        }
    )

    insights = generate_automated_insights(frame, high_correlation_threshold=0.8)

    assert any("Analyzed 5 rows across 3 columns" in insight for insight in insights)
    assert any("units: median 3" in insight for insight in insights)
    assert any("units and revenue: r=1.00" in insight for insight in insights)
    assert all("causal effects" not in insight for insight in insights[:-1])


def test_automated_insights_handle_empty_and_non_numeric_data() -> None:
    assert generate_automated_insights(pd.DataFrame()) == [
        "No rows are available for automated insights."
    ]
    assert generate_automated_insights(
        pd.DataFrame({"category": ["a", "b"]})
    ) == ["No numeric columns are available for distribution or correlation insights."]


@pytest.mark.parametrize("threshold", [0, -0.1, 1.1])
def test_automated_insights_reject_invalid_correlation_threshold(
    threshold: float,
) -> None:
    with pytest.raises(ValueError, match="Correlation threshold"):
        generate_automated_insights(
            pd.DataFrame({"x": [1, 2], "y": [2, 3]}),
            high_correlation_threshold=threshold,
        )

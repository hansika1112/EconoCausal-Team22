"""Small, descriptive EDA summaries for uploaded tabular datasets."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_automated_insights(
    frame: pd.DataFrame,
    *,
    high_correlation_threshold: float = 0.7,
    max_correlations: int = 5,
) -> list[str]:
    """Summarize distributions and strong numeric correlations without causal claims."""
    if not 0 < high_correlation_threshold <= 1:
        raise ValueError("Correlation threshold must be greater than 0 and at most 1.")
    if max_correlations < 1:
        raise ValueError("max_correlations must be at least 1.")
    if frame.empty:
        return ["No rows are available for automated insights."]

    numeric = frame.select_dtypes(include="number").replace(
        [np.inf, -np.inf], np.nan
    )
    numeric = numeric.dropna(axis=1, how="all")
    if numeric.empty:
        return ["No numeric columns are available for distribution or correlation insights."]

    insights = [
        f"Analyzed {len(frame):,} rows across {len(frame.columns):,} columns."
    ]
    for column in numeric.columns:
        values = numeric[column].dropna()
        if values.empty:
            continue
        skew = values.skew()
        distribution = "approximately symmetric"
        if pd.notna(skew) and skew > 0.5:
            distribution = "right-skewed"
        elif pd.notna(skew) and skew < -0.5:
            distribution = "left-skewed"
        insights.append(
            f"{column}: median {values.median():,.4g}, range "
            f"{values.min():,.4g} to {values.max():,.4g}; {distribution}."
        )

    if len(numeric.columns) >= 2 and len(frame) >= 2:
        correlations = numeric.corr(method="pearson")
        pairs: list[tuple[float, str, str]] = []
        columns = list(correlations.columns)
        for left_index, left in enumerate(columns):
            for right in columns[left_index + 1 :]:
                coefficient = correlations.at[left, right]
                if pd.notna(coefficient) and abs(float(coefficient)) >= high_correlation_threshold:
                    pairs.append((float(coefficient), str(left), str(right)))
        pairs.sort(key=lambda pair: abs(pair[0]), reverse=True)
        if pairs:
            strongest = pairs[:max_correlations]
            details = "; ".join(
                f"{left} and {right}: r={coefficient:.2f}"
                for coefficient, left, right in strongest
            )
            insights.append(
                f"High Pearson correlations (|r| >= "
                f"{high_correlation_threshold:.2f}): {details}. "
                "These are descriptive associations, not causal effects."
            )
        else:
            insights.append(
                f"No numeric feature pair reached |r| >= "
                f"{high_correlation_threshold:.2f}."
            )
    else:
        insights.append("At least two numeric features and rows are needed for correlations.")
    return insights

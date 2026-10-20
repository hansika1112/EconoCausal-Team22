from collections.abc import Sequence

import pandas as pd


def validate_dml_features(
    data: pd.DataFrame,
    treatment: str,
    outcome: str,
    confounders: Sequence[str] = (),
) -> dict:
    """Validate basic data readiness before fitting a DML model."""

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    if not treatment or not outcome:
        raise ValueError("Treatment and outcome names must be provided")

    if treatment == outcome:
        raise ValueError("Treatment and outcome must be different columns")

    if len(set(data.columns)) != len(data.columns):
        raise ValueError("DataFrame column names must be unique")

    if isinstance(confounders, str):
        raise TypeError("confounders must be a sequence of column names")

    if treatment in confounders or outcome in confounders:
        raise ValueError("Confounders must differ from treatment and outcome")

    if len(set(confounders)) != len(confounders):
        raise ValueError("Confounder names must be unique")

    required = [treatment, outcome, *confounders]
    missing = [column for column in required if column not in data.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    selected = data[required]
    numeric_columns = [treatment, outcome]

    non_numeric = [
        column for column in numeric_columns
        if not pd.api.types.is_numeric_dtype(selected[column])
    ]
    if non_numeric:
        raise TypeError(f"Treatment and outcome must be numeric: {non_numeric}")

    missing_counts = {
        column: int(selected[column].isna().sum())
        for column in required
    }

    return {
        "ready": all(count == 0 for count in missing_counts.values()),
        "row_count": int(len(data)),
        "treatment": treatment,
        "outcome": outcome,
        "confounders": list(confounders),
        "missing_counts": missing_counts,
        "complete_case_count": int(selected.dropna().shape[0]),
        "note": (
            "Readiness checks only. Passing these checks does not establish "
            "causal identification or validate the chosen confounders."
        ),
    }

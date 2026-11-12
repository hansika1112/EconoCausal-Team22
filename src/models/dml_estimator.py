from pathlib import Path

import numpy as np
import pandas as pd

from econml.dml import LinearDML
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.models.feature_readiness import validate_dml_features


TREATMENT = "log_price"
OUTCOME = "log_quantity"
CONFOUNDERS = ["StockCode", "Country", "month"]


def prepare_dml_data(data: pd.DataFrame) -> pd.DataFrame:
    """Prepare valid positive-sales observations for the DML pilot."""

    required = [
        "Invoice",
        "Price",
        "Quantity",
        TREATMENT,
        OUTCOME,
        *CONFOUNDERS,
    ]

    missing = [column for column in required if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    prepared = data[required].copy()

    prepared["Invoice"] = prepared["Invoice"].astype("string").str.strip()
    prepared["StockCode"] = prepared["StockCode"].astype("string")
    prepared["Country"] = prepared["Country"].astype("string")
    prepared["month"] = prepared["month"].astype("string")

    numeric = ["Price", "Quantity", TREATMENT, OUTCOME]
    for column in numeric:
        prepared[column] = pd.to_numeric(
            prepared[column], errors="coerce"
        )

    prepared = prepared.replace([np.inf, -np.inf], np.nan)
    prepared = prepared.dropna(subset=required)

    prepared = prepared.loc[
        (prepared["Price"] > 0)
        & (prepared["Quantity"] > 0)
    ].copy()

    if prepared.empty:
        raise ValueError("No valid observations remain after preparation.")

    if prepared["Invoice"].nunique() < 3:
        raise ValueError("At least three distinct invoices are required.")

    validation = validate_dml_features(
        prepared,
        treatment=TREATMENT,
        outcome=OUTCOME,
        confounders=CONFOUNDERS,
        require_positive=False,
    )

    if not validation["ready"]:
        raise ValueError(
            f"DML feature validation failed: {validation}"
        )

    return prepared.reset_index(drop=True)


def sample_by_invoice(
    data: pd.DataFrame,
    max_invoices: int = 1500,
    random_state: int = 42,
) -> pd.DataFrame:
    """Select complete invoices for a reproducible pilot sample."""

    if max_invoices < 3:
        raise ValueError("max_invoices must be at least 3.")

    invoice_ids = data["Invoice"].drop_duplicates().to_numpy()

    if len(invoice_ids) <= max_invoices:
        return data.copy().reset_index(drop=True)

    rng = np.random.default_rng(random_state)
    selected = rng.choice(
        invoice_ids,
        size=max_invoices,
        replace=False,
    )

    return (
        data.loc[data["Invoice"].isin(selected)]
        .copy()
        .reset_index(drop=True)
    )


def build_dml_estimator(n_splits: int = 3, random_state: int = 42):
    """Build a continuous-treatment LinearDML estimator."""

    if n_splits < 2:
        raise ValueError("n_splits must be at least 2.")

    model_y = Pipeline(
        steps=[
            (
                "encode",
                OneHotEncoder(
                    handle_unknown="ignore",
                    min_frequency=2,
                ),
            ),
            ("regressor", Ridge(alpha=10.0)),
        ]
    )

    model_t = Pipeline(
        steps=[
            (
                "encode",
                OneHotEncoder(
                    handle_unknown="ignore",
                    min_frequency=2,
                ),
            ),
            ("regressor", Ridge(alpha=10.0)),
        ]
    )

    return LinearDML(
        model_y=model_y,
        model_t=model_t,
        discrete_treatment=False,
        cv=GroupKFold(n_splits=n_splits),
        random_state=random_state,
    )


def fit_dml_model(
    data: pd.DataFrame,
    n_splits: int = 3,
    random_state: int = 42,
):
    """Fit DML using invoice-group-aware cross-fitting."""

    prepared = prepare_dml_data(data)

    if prepared["Invoice"].nunique() < n_splits:
        raise ValueError(
            "The number of unique invoices must be at least n_splits."
        )

    estimator = build_dml_estimator(
        n_splits=n_splits,
        random_state=random_state,
    )

    estimator.fit(
        Y=prepared[OUTCOME].to_numpy(),
        T=prepared[[TREATMENT]].to_numpy(),
        W=prepared[CONFOUNDERS],
        groups=prepared["Invoice"].to_numpy(),
        inference="auto",
    )

    return estimator, prepared


def run_pilot(
    csv_path: str | Path,
    max_invoices: int = 1500,
    n_splits: int = 3,
    random_state: int = 42,
):
    """Load the processed dataset and fit a reproducible pilot."""

    data = pd.read_csv(csv_path)
    prepared = prepare_dml_data(data)

    pilot = sample_by_invoice(
        prepared,
        max_invoices=max_invoices,
        random_state=random_state,
    )

    estimator, fitted_data = fit_dml_model(
        pilot,
        n_splits=n_splits,
        random_state=random_state,
    )

    inference = estimator.ate_inference()

    return {
        "estimator": estimator,
        "data": fitted_data,
        "inference": inference,
        "summary": {
            "rows": int(len(fitted_data)),
            "invoices": int(fitted_data["Invoice"].nunique()),
            "products": int(fitted_data["StockCode"].nunique()),
            "countries": int(fitted_data["Country"].nunique()),
            "months": int(fitted_data["month"].nunique()),
            "treatment": TREATMENT,
            "outcome": OUTCOME,
            "confounders": CONFOUNDERS,
            "estimator": "EconML LinearDML",
            "cross_fitting": "Invoice-group-aware GroupKFold",
            "interpretation": (
                "Observational DML estimate. Causal interpretation "
                "requires defensible identification assumptions."
            ),
        },
    }

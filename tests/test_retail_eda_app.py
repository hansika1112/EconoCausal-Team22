from io import BytesIO

import pandas as pd
import pytest

from src.data.retail_eda_app import (
    build_scaled_dataset,
    load_uploaded_data,
    preprocess_dataset,
)


@pytest.fixture
def transaction_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Invoice": ["10001", "10002"],
            "StockCode": ["A1", "A2"],
            "Quantity": [1, 3],
            "InvoiceDate": ["01/12/2010", "02/12/2010"],
            "Price": [2.0, 6.0],
        }
    )


def test_load_uploaded_csv_preserves_columns(transaction_frame: pd.DataFrame) -> None:
    content = transaction_frame.to_csv(index=False).encode("utf-8")

    loaded = load_uploaded_data(content, "transactions.csv")

    assert loaded.columns.tolist() == transaction_frame.columns.tolist()
    assert loaded["Invoice"].astype(str).tolist() == ["10001", "10002"]


def test_load_uploaded_json_as_records() -> None:
    content = b'[{"name":"Ada","score":2},{"name":"Lin","score":4}]'

    loaded = load_uploaded_data(content, "records.json")

    assert loaded.to_dict(orient="records") == [
        {"name": "Ada", "score": 2},
        {"name": "Lin", "score": 4},
    ]


def test_load_uploaded_json_from_nested_records_and_json_lines() -> None:
    wrapped = b'{"data":[{"name":"Ada"},{"name":"Lin"}]}'
    lines = b'{"name":"Ada"}\n{"name":"Lin"}\n'

    wrapped_frame = load_uploaded_data(wrapped, "wrapped.json")
    line_frame = load_uploaded_data(lines, "lines.json")

    assert wrapped_frame["name"].tolist() == ["Ada", "Lin"]
    assert line_frame["name"].tolist() == ["Ada", "Lin"]


def test_load_uploaded_excel_combines_sheets_and_selects_one(
    transaction_frame: pd.DataFrame,
) -> None:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        transaction_frame.iloc[:1].to_excel(writer, sheet_name="First", index=False)
        transaction_frame.iloc[1:].to_excel(writer, sheet_name="Second", index=False)
    content = buffer.getvalue()

    combined = load_uploaded_data(content, "transactions.xlsx")
    selected = load_uploaded_data(content, "transactions.xlsx", "Second")

    assert combined["Invoice"].astype(str).tolist() == ["10001", "10002"]
    assert selected["Invoice"].astype(str).tolist() == ["10002"]


def test_load_uploaded_data_rejects_unknown_workbook_sheet() -> None:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        pd.DataFrame({"Invoice": ["10001"]}).to_excel(
            writer, sheet_name="First", index=False
        )

    with pytest.raises(ValueError, match="does not contain"):
        load_uploaded_data(buffer.getvalue(), "transactions.xlsx", "Missing")


def test_build_scaled_dataset_appends_values_without_changing_source(
    transaction_frame: pd.DataFrame,
) -> None:
    transaction_frame["LineValue"] = (
        transaction_frame["Quantity"] * transaction_frame["Price"]
    )

    scaled = build_scaled_dataset(
        transaction_frame,
        ["Price", "Quantity"],
        "MinMaxScaler",
    )

    assert scaled["Price"].tolist() == [2.0, 6.0]
    assert scaled["Price_scaled"].tolist() == [0.0, 1.0]
    assert scaled["Quantity_scaled"].tolist() == [0.0, 1.0]


def test_build_scaled_dataset_rejects_non_finite_values(
    transaction_frame: pd.DataFrame,
) -> None:
    transaction_frame["Price"] = [2.0, float("inf")]

    with pytest.raises(ValueError, match="non-finite"):
        build_scaled_dataset(transaction_frame, ["Price"], "StandardScaler")


def test_build_scaled_dataset_does_not_overwrite_existing_scaled_column(
    transaction_frame: pd.DataFrame,
) -> None:
    transaction_frame["Price_scaled"] = [99.0, 100.0]

    with pytest.raises(ValueError, match="already exist"):
        build_scaled_dataset(transaction_frame, ["Price"], "StandardScaler")


def test_preprocess_dataset_imputes_numeric_and_categorical_independently() -> None:
    source = pd.DataFrame(
        {
            "amount": [1.0, None, 3.0],
            "category": ["a", None, "a"],
        }
    )

    result = preprocess_dataset(
        source,
        missing_action="Impute",
        missing_columns=["amount", "category"],
        numeric_impute_method="Median",
        categorical_impute_method="Mode",
    )

    assert result["amount"].tolist() == [1.0, 2.0, 3.0]
    assert result["category"].tolist() == ["a", "a", "a"]
    assert source.isna().sum().sum() == 2


def test_preprocess_dataset_imputes_nullable_integer_with_fractional_mean() -> None:
    source = pd.DataFrame({"amount": pd.Series([1, None, 2], dtype="Int64")})

    result = preprocess_dataset(
        source,
        missing_action="Impute",
        missing_columns=["amount"],
        numeric_impute_method="Mean",
    )

    assert result["amount"].tolist() == [1.0, 1.5, 2.0]


def test_preprocess_dataset_drops_duplicate_rows_and_missing_columns() -> None:
    source = pd.DataFrame(
        {
            "value": [1, 1, 2],
            "optional": [None, None, "present"],
        }
    )

    result = preprocess_dataset(
        source,
        missing_action="Drop columns",
        missing_columns=["optional"],
        drop_duplicates=True,
    )

    assert result.columns.tolist() == ["value"]
    assert result["value"].tolist() == [1, 2]


def test_preprocess_dataset_caps_iqr_outliers() -> None:
    source = pd.DataFrame({"value": [1, 2, 3, 4, 100]})

    result = preprocess_dataset(
        source,
        outlier_action="IQR capping",
        outlier_columns=["value"],
    )

    assert result["value"].tolist() == [1.0, 2.0, 3.0, 4.0, 7.0]


def test_preprocess_dataset_supports_z_score_filtering() -> None:
    source = pd.DataFrame({"value": [0.0] * 20 + [100.0]})

    result = preprocess_dataset(
        source,
        outlier_action="Z-score filtering",
        outlier_columns=["value"],
        z_score_threshold=3.0,
    )

    assert len(result) == 20
    assert result["value"].eq(0).all()


def test_preprocess_dataset_encodes_and_scales_selected_columns() -> None:
    source = pd.DataFrame(
        {
            "kind": ["a", "b", "a"],
            "value": [1.0, 2.0, 3.0],
        }
    )

    result = preprocess_dataset(
        source,
        encoding="One-Hot Encoding",
        categorical_columns=["kind"],
        scaling="Normalization (MinMaxScaler)",
        numeric_columns=["value"],
    )

    assert "kind_a" in result.columns
    assert "kind_b" in result.columns
    assert result["value"].tolist() == [0.0, 0.5, 1.0]


def test_preprocess_dataset_label_encodes_selected_categories() -> None:
    source = pd.DataFrame({"kind": ["blue", "red", None]})

    result = preprocess_dataset(
        source,
        encoding="Label Encoding",
        categorical_columns=["kind"],
    )

    assert result["kind"].tolist()[:2] == [0, 1]
    assert pd.isna(result["kind"].iloc[2])


def test_preprocess_dataset_label_encodes_all_missing_category() -> None:
    source = pd.DataFrame({"kind": [None, None]})

    result = preprocess_dataset(
        source,
        encoding="Label Encoding",
        categorical_columns=["kind"],
    )

    assert result["kind"].isna().all()

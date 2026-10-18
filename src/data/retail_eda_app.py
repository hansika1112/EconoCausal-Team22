"""Interactive Streamlit dashboard for the Online Retail II EDA workflow."""

from __future__ import annotations

import hashlib
import io
import json
import re
import zipfile
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler

from src.data.eda_insights import generate_automated_insights
from src.data.retail_eda import REQUIRED_COLUMNS, inspect_dataset, prepare_transactions

QUALITY_FLAGS = (
    "is_exact_duplicate",
    "is_cancellation",
    "is_return",
    "invalid_quantity",
    "invalid_price",
    "invalid_invoice_date",
    "missing_core_fields",
    "non_positive_quantity",
    "non_positive_price",
)
NUMERIC_COLUMNS = ("Quantity", "Price", "LineValue")
PAGES = (
    "Home / Dataset Upload",
    "Data Overview & Summary",
    "Data Preprocessing (Cleaning & Transformation)",
    "Exploratory Data Analysis (Visualizations)",
    "Export Cleaned Data",
)


def _read_json(file_bytes: bytes) -> pd.DataFrame:
    """Read JSON records, column-oriented objects, or newline-delimited JSON."""
    try:
        payload = json.loads(file_bytes.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        try:
            return pd.read_json(io.BytesIO(file_bytes), lines=True)
        except ValueError as exc:
            raise ValueError(f"Could not parse the uploaded JSON: {exc}") from exc
    if isinstance(payload, list):
        try:
            return pd.DataFrame(payload)
        except ValueError as exc:
            raise ValueError("JSON arrays must contain tabular records.") from exc
    if isinstance(payload, dict):
        for key in ("data", "records", "items", "results"):
            records = payload.get(key)
            if isinstance(records, list) and all(
                isinstance(record, dict) for record in records
            ):
                return pd.DataFrame(records)
        try:
            return pd.read_json(io.BytesIO(file_bytes))
        except ValueError:
            try:
                return pd.DataFrame(payload)
            except ValueError:
                return pd.DataFrame([payload])
    raise ValueError("JSON must contain a list of records or an object.")


def load_uploaded_data(
    file_bytes: bytes,
    file_name: str,
    sheet_name: str | None = None,
) -> pd.DataFrame:
    """Read a CSV or Excel upload and retain workbook sheet provenance."""
    suffix = Path(file_name).suffix.casefold()
    if suffix == ".csv":
        frame = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8-sig")
    elif suffix == ".json":
        frame = _read_json(file_bytes)
    elif suffix in {".xlsx", ".xlsm"}:
        workbook = pd.ExcelFile(io.BytesIO(file_bytes))
        selected_sheets = [sheet_name] if sheet_name is not None else workbook.sheet_names
        unknown_sheets = set(selected_sheets).difference(workbook.sheet_names)
        if unknown_sheets:
            raise ValueError(
                "Workbook does not contain sheet(s): "
                + ", ".join(sorted(unknown_sheets))
            )

        frames = []
        for name in selected_sheets:
            frame = workbook.parse(sheet_name=name)
            if frame.empty:
                continue
            frames.append(frame)
        if not frames:
            raise ValueError("The selected workbook sheets contain no transaction rows.")
        frame = pd.concat(frames, ignore_index=True, sort=False)
    else:
        raise ValueError("Upload a .csv, .xlsx, or .xlsm file.")

    if frame.empty:
        raise ValueError("The uploaded dataset contains no transaction rows.")
    return frame


def _is_retail_dataset(frame: pd.DataFrame) -> bool:
    aliases = {
        "invoice": "Invoice",
        "invoiceno": "Invoice",
        "invoicenumber": "Invoice",
        "stockcode": "StockCode",
        "quantity": "Quantity",
        "invoicedate": "InvoiceDate",
        "price": "Price",
        "unitprice": "Price",
    }
    canonical = {
        aliases.get(re.sub(r"[^a-z0-9]", "", str(column).casefold()))
        for column in frame.columns
    }
    return set(REQUIRED_COLUMNS).issubset(canonical)


def preprocess_dataset(
    frame: pd.DataFrame,
    *,
    missing_action: str = "Keep",
    missing_columns: list[str] | None = None,
    numeric_impute_method: str = "Mean",
    categorical_impute_method: str = "Mode",
    numeric_constant: float = 0.0,
    categorical_constant: str = "Missing",
    drop_duplicates: bool = False,
    outlier_action: str = "Keep",
    outlier_columns: list[str] | None = None,
    z_score_threshold: float = 3.0,
    encoding: str = "None",
    categorical_columns: list[str] | None = None,
    scaling: str = "None",
    numeric_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Apply user-selected cleaning and transformations to a copy of a dataset."""
    result = frame.copy()
    missing_columns = missing_columns or []
    outlier_columns = outlier_columns or []
    categorical_columns = categorical_columns or []
    numeric_columns = numeric_columns or []

    if missing_action == "Drop rows":
        selected = [column for column in missing_columns if column in result.columns]
        if selected:
            result = result.dropna(subset=selected)
    elif missing_action == "Drop columns":
        selected = [
            column
            for column in missing_columns
            if column in result.columns and result[column].isna().any()
        ]
        result = result.drop(columns=selected)
    elif missing_action == "Impute":
        for column in missing_columns:
            if column not in result.columns or not result[column].isna().any():
                continue
            if pd.api.types.is_numeric_dtype(result[column]):
                values = result[column].dropna()
                if values.empty:
                    raise ValueError(
                        f"Cannot impute '{column}' because it has no observed values."
                    )
                if numeric_impute_method == "Mean":
                    fill_value = values.mean()
                elif numeric_impute_method == "Median":
                    fill_value = values.median()
                elif numeric_impute_method == "Mode":
                    fill_value = values.mode().iloc[0]
                elif numeric_impute_method == "Constant":
                    fill_value = numeric_constant
                else:
                    raise ValueError(
                        f"Unsupported numeric imputation method: {numeric_impute_method}"
                    )
            else:
                if categorical_impute_method == "Constant":
                    fill_value = categorical_constant
                elif categorical_impute_method == "Mode":
                    modes = result[column].dropna().mode()
                    if modes.empty:
                        raise ValueError(
                            f"Cannot impute '{column}' because it has no observed values."
                        )
                    fill_value = modes.iloc[0]
                else:
                    raise ValueError(
                        "Categorical imputation supports Mode or Constant."
                    )
                if pd.api.types.is_datetime64_any_dtype(result[column]):
                    if categorical_impute_method == "Constant":
                        fill_value = pd.to_datetime(
                            fill_value,
                            errors="coerce",
                        )
                        if pd.isna(fill_value):
                            raise ValueError(
                                f"'{categorical_constant}' is not a valid date "
                                f"for column '{column}'."
                            )
                elif isinstance(result[column].dtype, pd.CategoricalDtype) or (
                    pd.api.types.is_bool_dtype(result[column])
                    and categorical_impute_method == "Constant"
                ):
                    result[column] = result[column].astype(object)
            if pd.api.types.is_numeric_dtype(result[column]):
                result[column] = (
                    pd.to_numeric(result[column], errors="coerce")
                    .astype(float)
                    .fillna(float(fill_value))
                )
            else:
                result[column] = result[column].fillna(fill_value)
    elif missing_action != "Keep":
        raise ValueError(f"Unsupported missing-value action: {missing_action}")

    if drop_duplicates:
        result = result.drop_duplicates().copy()

    if outlier_action == "IQR capping":
        for column in outlier_columns:
            if column not in result.columns:
                continue
            values = pd.to_numeric(result[column], errors="coerce")
            q1, q3 = values.quantile([0.25, 0.75])
            if pd.isna(q1) or pd.isna(q3):
                continue
            spread = q3 - q1
            result[column] = values.clip(q1 - 1.5 * spread, q3 + 1.5 * spread)
    elif outlier_action == "Z-score filtering":
        if z_score_threshold <= 0:
            raise ValueError("The Z-score threshold must be greater than zero.")
        z_scores = pd.DataFrame(index=result.index)
        for column in outlier_columns:
            if column not in result.columns:
                continue
            values = pd.to_numeric(result[column], errors="coerce")
            standard_deviation = values.std()
            if pd.isna(standard_deviation) or standard_deviation == 0:
                continue
            z_scores[column] = (values - values.mean()) / standard_deviation
        if not z_scores.empty:
            result = result.loc[
                ~z_scores.abs().gt(z_score_threshold).any(axis=1)
            ].copy()
    elif outlier_action != "Keep":
        raise ValueError(f"Unsupported outlier action: {outlier_action}")

    if encoding == "One-Hot Encoding":
        selected = [column for column in categorical_columns if column in result]
        if selected:
            result = pd.get_dummies(
                result,
                columns=selected,
                dummy_na=False,
                dtype=int,
            )
    elif encoding == "Label Encoding":
        for column in categorical_columns:
            if column not in result.columns:
                continue
            encoder = LabelEncoder()
            non_missing = result[column].notna()
            encoded = pd.Series(pd.NA, index=result.index, dtype="Int64")
            if non_missing.any():
                encoded.loc[non_missing] = encoder.fit_transform(
                    result.loc[non_missing, column].astype(str)
                )
            result[column] = encoded
    elif encoding != "None":
        raise ValueError(f"Unsupported encoding: {encoding}")

    selected_numeric = [column for column in numeric_columns if column in result]
    if scaling == "Standardization (StandardScaler)":
        scaler = StandardScaler()
    elif scaling == "Normalization (MinMaxScaler)":
        scaler = MinMaxScaler()
    elif scaling == "None":
        scaler = None
    else:
        raise ValueError(f"Unsupported scaling method: {scaling}")
    if scaler is not None and selected_numeric:
        values = result[selected_numeric].apply(pd.to_numeric, errors="coerce")
        if values.isna().any().any() or not np.isfinite(values.to_numpy()).all():
            raise ValueError("Selected columns contain missing or non-finite values.")
        result[selected_numeric] = scaler.fit_transform(values)

    return result


def build_scaled_dataset(
    frame: pd.DataFrame,
    columns: list[str],
    method: str,
) -> pd.DataFrame:
    """Append opt-in scaled columns while retaining their original values."""
    if frame.empty:
        raise ValueError("There are no analysis rows to scale.")
    if not columns:
        raise ValueError("Select at least one numeric column to scale.")
    if method == "StandardScaler":
        scaler = StandardScaler()
    elif method == "MinMaxScaler":
        scaler = MinMaxScaler()
    else:
        raise ValueError(f"Unsupported scaling method: {method}")

    output_columns = [f"{column}_scaled" for column in columns]
    collisions = sorted(set(output_columns).intersection(frame.columns))
    if collisions:
        raise ValueError(
            "Scaled output columns already exist: " + ", ".join(collisions)
        )
    values = frame[columns].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Selected columns contain non-finite values and cannot be scaled.")

    result = frame.copy()
    scaled_values = scaler.fit_transform(values)
    for position, column in enumerate(columns):
        result[f"{column}_scaled"] = scaled_values[:, position]
    return result


@st.cache_data(show_spinner="Preparing the uploaded transactions...")
def _prepare_upload(
    file_bytes: bytes,
    file_name: str,
    sheet_name: str | None,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    bool,
]:
    raw = load_uploaded_data(file_bytes, file_name, sheet_name)
    is_retail = _is_retail_dataset(raw)
    if is_retail:
        normalized, sample, audit, issue_counts = prepare_transactions(raw)
    else:
        normalized = raw.copy()
        sample = raw.copy()
        audit = pd.DataFrame(
            columns=("step", "rows_removed", "rows_remaining")
        )
        issue_counts = pd.DataFrame(columns=("issue", "row_count", "row_pct"))
    return raw, normalized, sample, audit, issue_counts, is_retail


def _render_sidebar() -> tuple[str, object, str | None]:
    with st.sidebar:
        st.title("Data Prep Studio")
        st.caption("Preprocessing & analytics")
        page = st.radio(
            "Navigate",
            PAGES,
            label_visibility="collapsed",
        )
        st.divider()
        st.subheader("Dataset")
        uploaded_file = st.file_uploader(
            "Upload transactions",
            type=["csv", "xlsx", "xlsm", "json"],
            help="CSV, Excel, and JSON files are supported.",
        )

        selected_sheet: str | None = None
        if uploaded_file and Path(uploaded_file.name).suffix.casefold() in {
            ".xlsx",
            ".xlsm",
        }:
            try:
                sheet_names = pd.ExcelFile(
                    io.BytesIO(uploaded_file.getvalue())
                ).sheet_names
            except (ValueError, OSError, zipfile.BadZipFile) as exc:
                st.error(f"Could not read this workbook: {exc}")
                st.stop()
            sheet_choice = st.selectbox("Workbook sheets", ["All sheets", *sheet_names])
            if sheet_choice != "All sheets":
                selected_sheet = sheet_choice
    return page, uploaded_file, selected_sheet


def _filter_analysis_sample(sample: pd.DataFrame) -> pd.DataFrame:
    filtered = sample.copy()
    with st.sidebar:
        st.divider()
        st.subheader("EDA filters")
        if "Country" in sample.columns:
            available_countries = sorted(
                sample["Country"].dropna().astype(str).unique().tolist()
            )
            countries = st.multiselect("Countries", available_countries)
            if countries:
                filtered = filtered.loc[
                    filtered["Country"].astype(str).isin(countries)
                ]

        if "InvoiceDate" in sample.columns and not sample.empty:
            dates = pd.to_datetime(sample["InvoiceDate"], errors="coerce").dropna()
        else:
            dates = pd.Series(dtype="datetime64[ns]")
        if not dates.empty:
            earliest = dates.min().date()
            latest = dates.max().date()
            date_range = st.date_input(
                "Invoice date range",
                value=(earliest, latest),
                min_value=earliest,
                max_value=latest,
            )
            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date, end_date = date_range
                if start_date is not None and end_date is not None:
                    filtered = filtered.loc[
                        pd.to_datetime(
                            filtered["InvoiceDate"], errors="coerce"
                        ).ge(pd.Timestamp(start_date))
                        & pd.to_datetime(
                            filtered["InvoiceDate"], errors="coerce"
                        ).lt(
                            pd.Timestamp(end_date) + pd.Timedelta(days=1)
                        )
                    ]

        if "StockCode" in sample.columns:
            stock_counts = sample["StockCode"].value_counts().head(100)
            products = st.multiselect(
                "Product codes (top 100)",
                stock_counts.index.astype(str).tolist(),
            )
            if products:
                filtered = filtered.loc[
                    filtered["StockCode"].astype(str).isin(products)
                ]
    return filtered


def _render_home(
    uploaded_file: object,
    raw: pd.DataFrame | None,
    sample: pd.DataFrame | None,
    is_retail: bool,
) -> None:
    st.title("Data Prep Studio")
    st.write(
        "A guided workspace to upload, inspect, preprocess, explore, and export "
        "your dataset."
    )
    if uploaded_file is None:
        st.info("Upload a CSV, Excel, or JSON file using the sidebar to get started.")
    else:
        st.success(f"Loaded **{uploaded_file.name}**")
        if raw is not None and sample is not None:
            first, second, third = st.columns(3)
            first.metric("Source rows", f"{len(raw):,}")
            second.metric("Analysis rows", f"{len(sample):,}")
            third.metric("Columns", str(raw.shape[1]))
            st.dataframe(raw.head(10), hide_index=True, use_container_width=True)

    st.markdown(
        """
        **Workflow**
        1. Upload a CSV, Excel, or JSON dataset and choose a workbook sheet if needed.
        2. Review its dimensions and descriptive statistics in **Data Overview & Summary**.
        3. Inspect cleaning decisions and optional scaling in **Data Preprocessing**.
        4. Explore filtered, interactive charts in **Exploratory Data Analysis**.
        5. Download normalized or cleaned data from **Export Cleaned Data**.

        Retail transaction columns (Invoice, StockCode, Quantity, InvoiceDate,
        and Price) activate the retail-specific audit. Other tabular files are
        processed as general-purpose datasets. Original rows are not overwritten,
        and cleaning does not establish causal validity.
        """
    )
    if uploaded_file is not None and not is_retail:
        st.caption("This upload is being handled as a general-purpose dataset.")


def _render_overview(
    raw: pd.DataFrame,
    normalized: pd.DataFrame,
    sample: pd.DataFrame,
) -> None:
    st.title("Data Overview & Summary")
    source = raw
    metric_columns = st.columns(4)
    metric_columns[0].metric("Total Rows", f"{len(source):,}")
    metric_columns[1].metric("Total Columns", str(source.shape[1]))
    metric_columns[2].metric(
        "Memory",
        f"{source.memory_usage(index=True, deep=True).sum() / (1024 ** 2):,.2f} MiB",
    )
    metric_columns[3].metric("Eligible analysis rows", f"{len(sample):,}")
    quality_metrics = st.columns(2)
    quality_metrics[0].metric("Missing values", f"{int(source.isna().sum().sum()):,}")
    quality_metrics[1].metric("Duplicate rows", f"{int(source.duplicated().sum()):,}")

    st.subheader("Dataset shape and data types")
    st.write(f"**Shape:** {source.shape[0]:,} rows × {source.shape[1]:,} columns")
    dtypes = pd.DataFrame(
        {"Column": source.columns.astype(str), "Data type": source.dtypes.astype(str).values}
    )
    st.dataframe(dtypes, hide_index=True, use_container_width=True)
    first, last = st.columns(2)
    with first:
        st.markdown("**First five rows**")
        st.dataframe(source.head(5), hide_index=True, use_container_width=True)
    with last:
        st.markdown("**Last five rows**")
        st.dataframe(source.tail(5), hide_index=True, use_container_width=True)
    _, column_audit = inspect_dataset(source)
    with st.expander("Column names, data types, and formatting audit"):
        st.dataframe(column_audit, hide_index=True, use_container_width=True)

    st.subheader("Analysis sample summary")
    numeric_columns = sample.select_dtypes(include="number").columns.tolist()
    if sample.empty or not numeric_columns:
        st.info("No numeric columns are available for a statistical summary.")
    else:
        st.dataframe(sample[numeric_columns].describe().T, use_container_width=True)
        if "InvoiceDate" in sample:
            dates = pd.to_datetime(sample["InvoiceDate"], errors="coerce").dropna()
            if not dates.empty:
                st.caption(
                    f"Eligible invoice dates: {dates.min():%Y-%m-%d} to "
                    f"{dates.max():%Y-%m-%d}."
                )
    st.caption(
        f"Records retained for preprocessing: {len(normalized):,}. "
        "Optional missing values are not imputed."
    )


def _render_preprocessing(
    source: pd.DataFrame,
    processed: pd.DataFrame,
    on_apply: Callable[[pd.DataFrame], None],
    audit: pd.DataFrame,
    issue_counts: pd.DataFrame,
) -> pd.DataFrame:
    st.title("Data Preprocessing (Cleaning & Transformation)")
    st.write(
        "Configure steps and apply them to a copy of the analysis input. "
        "Applied results persist for this upload until its file or sheet changes."
    )
    if not audit.empty:
        with st.expander("Retail positive-sales cleaning audit"):
            st.dataframe(audit, hide_index=True, use_container_width=True)
            st.dataframe(issue_counts, hide_index=True, use_container_width=True)
    missing_columns_with_values = source.columns[source.isna().any()].tolist()
    with st.expander("Missing value handling", expanded=True):
        missing_action = st.selectbox(
            "Action",
            ["Keep", "Drop rows", "Drop columns", "Impute"],
        )
        missing_columns = st.multiselect(
            "Columns to check or impute",
            source.columns.tolist(),
            default=missing_columns_with_values,
        )
        numeric_impute_method = "Mean"
        categorical_impute_method = "Mode"
        numeric_constant = 0.0
        categorical_constant = "Missing"
        if missing_action == "Impute":
            numeric, categorical = st.columns(2)
            with numeric:
                numeric_impute_method = st.selectbox(
                    "Numerical imputation",
                    ["Mean", "Median", "Mode", "Constant"],
                )
                if numeric_impute_method == "Constant":
                    numeric_constant = st.number_input(
                        "Numerical constant",
                        value=0.0,
                    )
            with categorical:
                categorical_impute_method = st.selectbox(
                    "Categorical imputation",
                    ["Mode", "Constant"],
                )
                if categorical_impute_method == "Constant":
                    categorical_constant = st.text_input(
                        "Categorical constant",
                        value="Missing",
                    )

    drop_duplicates = st.checkbox(
        "Automatically drop duplicate rows",
        value=False,
    )
    numeric_source = source.select_dtypes(include="number").columns.tolist()
    st.subheader("Outlier detection and treatment")
    outlier_columns = st.multiselect(
        "Numerical columns to check",
        numeric_source,
        default=numeric_source,
    )
    if outlier_columns:
        st.plotly_chart(
            px.box(
                source.melt(
                    value_vars=outlier_columns,
                    var_name="Feature",
                    value_name="Value",
                ),
                x="Feature",
                y="Value",
                points="outliers",
                title="Outlier review (before treatment)",
            ),
            use_container_width=True,
        )
    outlier_action = st.selectbox(
        "Outlier treatment",
        ["Keep", "IQR capping", "Z-score filtering"],
    )
    z_score_threshold = 3.0
    if outlier_action == "Z-score filtering":
        z_score_threshold = st.number_input(
            "Absolute Z-score threshold",
            min_value=0.1,
            value=3.0,
            step=0.5,
        )

    categorical_source = source.select_dtypes(
        include=["object", "category", "string", "bool"]
    ).columns.tolist()
    st.subheader("Categorical feature encoding")
    encoding = st.selectbox(
        "Encoding method",
        ["None", "One-Hot Encoding", "Label Encoding"],
    )
    categorical_columns = st.multiselect(
        "Categorical columns to encode",
        categorical_source,
        default=[],
        disabled=encoding == "None",
    )

    st.subheader("Numerical feature scaling")
    scaling = st.selectbox(
        "Scaling method",
        [
            "None",
            "Standardization (StandardScaler)",
            "Normalization (MinMaxScaler)",
        ],
    )
    scale_candidates = [
        column for column in numeric_source if column not in QUALITY_FLAGS
    ]
    if encoding == "Label Encoding":
        scale_candidates.extend(
            column for column in categorical_columns if column not in scale_candidates
        )
    numeric_columns = st.multiselect(
        "Numerical columns to scale",
        scale_candidates,
        default=[],
        disabled=scaling == "None",
    )

    if st.button("Apply preprocessing", type="primary"):
        try:
            result = preprocess_dataset(
                source,
                missing_action=missing_action,
                missing_columns=missing_columns,
                numeric_impute_method=numeric_impute_method,
                categorical_impute_method=categorical_impute_method,
                numeric_constant=numeric_constant,
                categorical_constant=categorical_constant,
                drop_duplicates=drop_duplicates,
                outlier_action=outlier_action,
                outlier_columns=outlier_columns,
                z_score_threshold=z_score_threshold,
                encoding=encoding,
                categorical_columns=categorical_columns,
                scaling=scaling,
                numeric_columns=numeric_columns,
            )
        except (KeyError, TypeError, ValueError) as exc:
            st.error(f"Could not apply preprocessing: {exc}")
        else:
            on_apply(result)
            st.success(
                f"Preprocessing applied: {len(source):,} input rows, "
                f"{len(result):,} output rows."
            )
            processed = result

    st.subheader("Processed data preview")
    st.dataframe(processed.head(100), hide_index=True, use_container_width=True)
    return processed


def _render_eda(filtered: pd.DataFrame) -> None:
    st.title("Exploratory Data Analysis (Visualizations)")
    if filtered.empty:
        st.info("No eligible rows match the selected sidebar filters.")
        return

    st.subheader("Univariate analysis")
    numeric = filtered.select_dtypes(include="number").columns.tolist()
    categorical = filtered.select_dtypes(
        include=["object", "category", "string", "bool"]
    ).columns.tolist()
    all_columns = [*numeric, *categorical]
    if not all_columns:
        st.info("No supported numerical or categorical columns are available.")
        return

    univariate_column = st.selectbox("Select a feature", all_columns)
    if univariate_column in numeric:
        univariate_type = st.radio(
            "Univariate visualization",
            ["Histogram", "Boxplot"],
            horizontal=True,
        )
        if univariate_type == "Histogram":
            st.plotly_chart(
                px.histogram(
                    filtered,
                    x=univariate_column,
                    nbins=40,
                    title=f"{univariate_column} distribution",
                ),
                use_container_width=True,
            )
        else:
            st.plotly_chart(
                px.box(
                    filtered,
                    y=univariate_column,
                    points="outliers",
                    title=f"{univariate_column} boxplot",
                ),
                use_container_width=True,
            )
    else:
        counts = (
            filtered[univariate_column]
            .fillna("(missing)")
            .astype(str)
            .value_counts()
            .head(30)
            .rename_axis(univariate_column)
            .reset_index(name="Rows")
        )
        st.plotly_chart(
            px.bar(
                counts,
                x="Rows",
                y=univariate_column,
                orientation="h",
                title=f"{univariate_column} category counts",
            ),
            use_container_width=True,
        )

    if numeric:
        st.subheader("Bivariate and grouped analysis")
    if len(numeric) >= 2:
        first, second = st.columns(2)
        with first:
            x_column = st.selectbox("X feature", numeric, index=0)
        y_options = [column for column in numeric if column != x_column]
        with second:
            y_column = st.selectbox("Y feature", y_options, index=0)
        color_options = ["None", *categorical]
        color_column = st.selectbox("Scatter color / group", color_options)
        plot_frame = filtered[[x_column, y_column]].copy()
        if color_column != "None":
            plot_frame[color_column] = filtered[color_column]
        plot_frame = plot_frame.replace([np.inf, -np.inf], np.nan).dropna(
            subset=[x_column, y_column]
        )
        if len(plot_frame) > 10_000:
            plot_frame = plot_frame.sample(n=10_000, random_state=42)
        if plot_frame.empty:
            st.info("The selected numeric pair has no finite observations.")
        else:
            scatter = px.scatter(
                plot_frame,
                x=x_column,
                y=y_column,
                color=color_column if color_column != "None" else None,
                title=f"{x_column} vs {y_column}",
                opacity=0.65,
            )
            pair = plot_frame[[x_column, y_column]].dropna()
            if len(pair) >= 2 and pair[x_column].nunique() > 1:
                slope, intercept = np.polyfit(
                    pair[x_column].to_numpy(dtype=float),
                    pair[y_column].to_numpy(dtype=float),
                    1,
                )
                x_line = np.linspace(pair[x_column].min(), pair[x_column].max(), 100)
                scatter.add_scatter(
                    x=x_line,
                    y=slope * x_line + intercept,
                    mode="lines",
                    name="Linear trend",
                )
            st.plotly_chart(scatter, use_container_width=True)
    else:
        st.info("Select a dataset with at least two numeric columns for scatter analysis.")

    if numeric and categorical:
        grouped_left, grouped_right = st.columns(2)
        with grouped_left:
            group_column = st.selectbox("Group by", categorical)
        with grouped_right:
            measure_column = st.selectbox("Measure", numeric)
        aggregation = st.selectbox(
            "Grouped aggregation",
            ["Mean", "Sum", "Median", "Count"],
        )
        group_frame = filtered[[group_column, measure_column]].copy()
        group_frame[group_column] = group_frame[group_column].fillna("(missing)").astype(str)
        if aggregation == "Mean":
            grouped = group_frame.groupby(group_column)[measure_column].mean()
        elif aggregation == "Sum":
            grouped = group_frame.groupby(group_column)[measure_column].sum()
        elif aggregation == "Median":
            grouped = group_frame.groupby(group_column)[measure_column].median()
        else:
            grouped = group_frame.groupby(group_column)[measure_column].count()
        grouped = grouped.sort_values(ascending=False).head(30)
        grouped_frame = grouped.rename("Value").reset_index()
        st.plotly_chart(
            px.bar(
                grouped_frame,
                x=group_column,
                y="Value",
                title=f"{aggregation} {measure_column} by {group_column}",
            ),
            use_container_width=True,
        )

    if len(numeric) >= 2:
        st.subheader("Correlation matrix")
        selected_numeric = st.multiselect(
            "Numerical features",
            numeric,
            default=numeric[: min(len(numeric), 12)],
        )
        if len(selected_numeric) >= 2:
            correlations = filtered[selected_numeric].corr(method="pearson")
            st.plotly_chart(
                px.imshow(
                    correlations,
                    text_auto=".2f",
                    zmin=-1,
                    zmax=1,
                    color_continuous_scale="RdBu_r",
                    title="Pearson correlation coefficients",
                ),
                use_container_width=True,
            )
        else:
            st.info("Select at least two numeric features for the correlation matrix.")

    st.subheader("Automated insights")
    threshold = st.slider(
        "High-correlation threshold (absolute Pearson r)",
        min_value=0.3,
        max_value=1.0,
        value=0.7,
        step=0.05,
    )
    for insight in generate_automated_insights(
        filtered,
        high_correlation_threshold=threshold,
    ):
        st.markdown(f"- {insight}")
    st.caption(
        "Insights and visualizations describe patterns in this data; they do not "
        "establish causality. Gross line value, when present, is a mechanical "
        "product of price and quantity."
    )


def _render_export(normalized: pd.DataFrame, processed: pd.DataFrame) -> None:
    st.title("Export Cleaned Data")
    st.write(
        "Download the latest dataset produced by the selected preprocessing "
        "steps, or inspect the unmodified normalized input."
    )
    st.metric("Cleaned rows", f"{len(processed):,}")
    st.download_button(
        "Download cleaned data (CSV)",
        data=processed.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        "Download all normalized rows and quality flags (CSV)",
        data=normalized.to_csv(index=False).encode("utf-8"),
        file_name="normalized_transactions.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.subheader("Preview cleaned data")
    st.dataframe(processed.head(100), hide_index=True, use_container_width=True)
    st.caption(
        "Preprocessing is applied to a working copy. The uploaded and normalized "
        "data remain available and are never overwritten."
    )


def main() -> None:
    st.set_page_config(
        page_title="Data Prep Studio",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .stApp { background: #f5f7fb; }
        [data-testid="stSidebar"] { background: #111827; }
        [data-testid="stSidebar"] * { color: #f8fafc; }
        .block-container { padding-top: 2rem; padding-bottom: 3rem; }
        div[data-testid="stMetric"] {
            background: #ffffff; border: 1px solid #e7ebf2;
            padding: 1rem 1.2rem; border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    page, uploaded_file, selected_sheet = _render_sidebar()
    if uploaded_file is None:
        if page == PAGES[0]:
            _render_home(None, None, None, False)
        else:
            st.title(page)
            st.info("Upload a CSV, Excel, or JSON file from the sidebar to continue.")
        return

    file_bytes = uploaded_file.getvalue()
    try:
        raw, normalized, sample, audit, issue_counts, is_retail = _prepare_upload(
            file_bytes,
            uploaded_file.name,
            selected_sheet,
        )
    except (
        ValueError,
        OSError,
        zipfile.BadZipFile,
        pd.errors.ParserError,
        pd.errors.EmptyDataError,
    ) as exc:
        st.error(f"Could not process this dataset: {exc}")
        st.stop()

    dataset_key = hashlib.sha256(
        uploaded_file.name.encode("utf-8")
        + b"\0"
        + file_bytes
        + b"\0"
        + (selected_sheet or "").encode("utf-8")
    ).hexdigest()
    if st.session_state.get("active_dataset_key") != dataset_key:
        st.session_state["active_dataset_key"] = dataset_key
        baseline = sample.copy()
        st.session_state["preprocessing_source"] = baseline
        st.session_state["processed_dataset"] = baseline.copy()
        for widget_key in (
            "missing_action",
            "missing_columns",
            "outlier_columns",
        ):
            st.session_state.pop(widget_key, None)
    preprocessing_source = st.session_state["preprocessing_source"]
    processed = st.session_state["processed_dataset"]

    if page == PAGES[0]:
        _render_home(uploaded_file, raw, sample, is_retail)
    elif page == PAGES[1]:
        _render_overview(raw, normalized, sample)
    elif page == PAGES[2]:
        def save_processed(frame: pd.DataFrame) -> None:
            st.session_state["processed_dataset"] = frame

        _render_preprocessing(
            preprocessing_source,
            processed,
            save_processed,
            audit,
            issue_counts,
        )
    elif page == PAGES[3]:
        _render_eda(_filter_analysis_sample(processed))
    else:
        _render_export(normalized, processed)


if __name__ == "__main__":
    main()

"""Preprocessing and exploratory analysis for the provisional Online Retail II data."""

from __future__ import annotations

import argparse
import io
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

REQUIRED_COLUMNS = ("Invoice", "StockCode", "Quantity", "InvoiceDate", "Price")
OPTIONAL_COLUMNS = ("Description", "Customer ID", "Country")
COLUMN_ALIASES = {
    "invoice": "Invoice",
    "invoiceno": "Invoice",
    "invoicenumber": "Invoice",
    "stockcode": "StockCode",
    "quantity": "Quantity",
    "invoicedate": "InvoiceDate",
    "price": "Price",
    "unitprice": "Price",
    "description": "Description",
    "customerid": "Customer ID",
    "country": "Country",
}


def _column_key(column: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(column).casefold())


def inspect_dataset(frame: pd.DataFrame) -> tuple[str, pd.DataFrame]:
    """Describe a source frame and flag column-label formatting inconsistencies."""
    info_buffer = io.StringIO()
    frame.info(buf=info_buffer, memory_usage="deep")

    column_rows: list[dict[str, Any]] = []
    normalized_names: dict[str, list[str]] = {}
    canonical_names: dict[str, list[str]] = {}
    duplicate_labels = frame.columns.duplicated(keep=False)
    for position, column in enumerate(frame.columns):
        label = str(column)
        trimmed = label.strip()
        key = _column_key(trimmed)
        canonical = COLUMN_ALIASES.get(key)
        issues: list[str] = []
        if not isinstance(column, str):
            issues.append("column label is not a string")
        if label != trimmed:
            issues.append("leading or trailing whitespace")
        if not trimmed:
            issues.append("empty column name")
        if re.search(r"\s{2,}", trimmed):
            issues.append("repeated internal whitespace")
        if duplicate_labels[position]:
            issues.append("duplicate column label")
        if key in normalized_names:
            issues.append("duplicates another name after formatting normalization")
        if canonical is not None and canonical != label:
            issues.append(f"recognized alias for {canonical}")

        normalized_names.setdefault(key, []).append(label)
        if canonical is not None:
            canonical_names.setdefault(canonical, []).append(label)
        column_rows.append(
            {
                "original_name": label,
                "trimmed_name": trimmed,
                "canonical_name": canonical or "",
                "dtype": str(frame.dtypes.iloc[position]),
                "format_issues": "; ".join(issues),
            }
        )

    for row in column_rows:
        canonical = row["canonical_name"]
        if canonical and len(canonical_names[canonical]) > 1:
            collision = f"multiple columns map to {canonical}"
            row["format_issues"] = (
                f"{row['format_issues']}; {collision}".lstrip("; ")
            )

    column_audit = pd.DataFrame(
        column_rows,
        columns=(
            "original_name",
            "trimmed_name",
            "canonical_name",
            "dtype",
            "format_issues",
        ),
    )
    memory_bytes = int(frame.memory_usage(index=True, deep=True).sum())
    description = frame.describe(include="all").transpose().to_string()
    report = f"""Dataset dimensions: {frame.shape[0]:,} rows × {frame.shape[1]:,} columns
Memory usage (deep, including index): {memory_bytes:,} bytes ({memory_bytes / (1024 ** 2):.2f} MiB)

DataFrame.info():
{info_buffer.getvalue().rstrip()}

Column names and formatting audit:
{column_audit.to_string(index=False)}

First five rows:
{frame.head().to_string(index=False)}

Last five rows:
{frame.tail().to_string(index=False)}

Statistical summary (describe(include="all"), transposed):
{description}
"""
    return report, column_audit


def _write_initial_inspection(
    frames: list[tuple[str, pd.DataFrame]], output_dir: Path
) -> None:
    inspection_dir = output_dir / "initial_inspection"
    inspection_dir.mkdir(parents=True, exist_ok=True)
    all_audits: list[pd.DataFrame] = []
    for index, (source_sheet, frame) in enumerate(frames, start=1):
        report, audit = inspect_dataset(frame)
        safe_sheet = re.sub(r"[^A-Za-z0-9_-]+", "_", source_sheet).strip("_")
        filename = f"{index:02d}_{safe_sheet or 'source'}.txt"
        (inspection_dir / filename).write_text(report, encoding="utf-8")
        sheet_audit = audit.copy()
        sheet_audit.insert(0, "source_sheet", source_sheet)
        all_audits.append(sheet_audit)

    pd.concat(all_audits, ignore_index=True).to_csv(
        inspection_dir / "column_format_audit.csv", index=False
    )


def _canonicalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    rename: dict[object, str] = {}
    canonical_seen: set[str] = set()
    for column in frame.columns:
        canonical = COLUMN_ALIASES.get(_column_key(column))
        if canonical is None:
            continue
        if canonical in canonical_seen:
            raise ValueError(f"Multiple input columns map to {canonical!r}.")
        canonical_seen.add(canonical)
        rename[column] = canonical

    result = frame.rename(columns=rename).copy()
    missing = [column for column in REQUIRED_COLUMNS if column not in result.columns]
    if missing:
        raise ValueError(
            "Input is missing required Online Retail II columns: "
            + ", ".join(missing)
        )
    for column in OPTIONAL_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    return result


def load_transactions(
    input_path: str | Path,
    sheet_name: str | None = None,
    inspection_dir: str | Path | None = None,
) -> pd.DataFrame:
    """Load transactions, optionally recording inspection before name normalization."""
    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file does not exist: {path}")

    if path.suffix.casefold() == ".csv":
        frames = [("CSV", pd.read_csv(path, encoding="utf-8-sig"))]
    elif path.suffix.casefold() in {".xlsx", ".xlsm"}:
        workbook = pd.ExcelFile(path)
        selected_sheets = [sheet_name] if sheet_name is not None else workbook.sheet_names
        unknown_sheets = set(selected_sheets).difference(workbook.sheet_names)
        if unknown_sheets:
            raise ValueError(
                f"Workbook does not contain sheet(s): {', '.join(sorted(unknown_sheets))}"
            )
        frames = [
            (name, workbook.parse(sheet_name=name))
            for name in selected_sheets
        ]
    else:
        raise ValueError("Supported input formats are .csv, .xlsx, and .xlsm.")

    if inspection_dir is not None:
        _write_initial_inspection(frames, Path(inspection_dir))

    normalized: list[pd.DataFrame] = []
    for source_sheet, frame in frames:
        if frame.empty:
            continue
        current = _canonicalize_columns(frame)
        current["source_sheet"] = source_sheet
        normalized.append(current)
    if not normalized:
        raise ValueError("The selected input contains no transaction rows.")
    return pd.concat(normalized, ignore_index=True, sort=False)


def prepare_transactions(
    raw: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Normalize fields and build an auditable positive-sales analysis sample.

    The normalized output retains every source row. Only the separate analysis
    sample excludes exact duplicates, cancellations, invalid core fields,
    returns/non-positive quantities, and non-positive prices.
    """
    transactions = _canonicalize_columns(raw)
    transactions["Invoice"] = transactions["Invoice"].astype("string").str.strip()
    transactions["StockCode"] = transactions["StockCode"].astype("string").str.strip()
    transactions["Invoice"] = transactions["Invoice"].replace("", pd.NA)
    transactions["StockCode"] = transactions["StockCode"].replace("", pd.NA)
    for column in ("Description", "Country"):
        transactions[column] = transactions[column].astype("string").str.strip()

    for column in ("Quantity", "Price"):
        parsed = pd.to_numeric(transactions[column], errors="coerce")
        transactions[f"invalid_{column.casefold()}"] = (
            transactions[column].notna() & parsed.isna()
        )
        transactions[column] = parsed

    source_dates = transactions["InvoiceDate"].copy()
    parsed_dates = pd.to_datetime(source_dates, errors="coerce", dayfirst=True)
    transactions["invalid_invoice_date"] = (
        source_dates.notna() & parsed_dates.isna()
    )
    transactions["InvoiceDate"] = parsed_dates

    invoice_text = transactions["Invoice"].fillna("")
    transactions["is_cancellation"] = invoice_text.str.upper().str.startswith("C")
    transactions["is_return"] = transactions["Quantity"].lt(0).fillna(False)
    transactions["non_positive_quantity"] = transactions["Quantity"].le(0).fillna(False)
    transactions["non_positive_price"] = transactions["Price"].le(0).fillna(False)
    transactions["missing_core_fields"] = transactions[list(REQUIRED_COLUMNS)].isna().any(axis=1)

    duplicate_columns = [
        column for column in transactions.columns if column != "source_sheet"
    ]
    transactions["is_exact_duplicate"] = transactions.duplicated(
        subset=duplicate_columns, keep="first"
    )

    sample_mask = ~transactions["is_exact_duplicate"]
    audit_rows: list[dict[str, int | str]] = [
        {"step": "Source rows", "rows_removed": 0, "rows_remaining": len(transactions)}
    ]
    exclusions = (
        ("Exact duplicate rows", "is_exact_duplicate"),
        ("Cancellation invoices", "is_cancellation"),
        ("Missing or invalid core fields", "missing_core_fields"),
        ("Non-positive quantities (including returns)", "non_positive_quantity"),
        ("Non-positive prices", "non_positive_price"),
    )
    for label, flag in exclusions:
        before = int(sample_mask.sum())
        sample_mask &= ~transactions[flag]
        remaining = int(sample_mask.sum())
        audit_rows.append(
            {
                "step": label,
                "rows_removed": before - remaining,
                "rows_remaining": remaining,
            }
        )

    analysis_sample = transactions.loc[sample_mask].copy()
    analysis_sample["LineValue"] = (
        analysis_sample["Quantity"] * analysis_sample["Price"]
    )
    cleaning_audit = pd.DataFrame(audit_rows)
    issue_flags = (
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
    issue_counts = pd.DataFrame(
        [
            {
                "issue": flag,
                "row_count": int(transactions[flag].sum()),
                "row_pct": (
                    float(transactions[flag].mean() * 100)
                    if len(transactions)
                    else 0.0
                ),
            }
            for flag in issue_flags
        ]
    )
    return transactions, analysis_sample, cleaning_audit, issue_counts


def _save_plots(sample: pd.DataFrame, figure_dir: Path) -> list[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    if sample.empty:
        return []

    saved: list[str] = []

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].hist(sample["Price"], bins=50, color="#4472C4")
    axes[0].set(title="Unit price distribution", xlabel="Price", ylabel="Line count")
    axes[1].hist(sample["Quantity"], bins=50, color="#70AD47")
    axes[1].set(
        title="Quantity distribution", xlabel="Quantity", ylabel="Line count"
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "positive_price_quantity_distributions.png", dpi=150)
    plt.close(fig)
    saved.append("positive_price_quantity_distributions.png")

    numeric_columns = ("Price", "Quantity", "LineValue")
    fig, axes = plt.subplots(1, len(numeric_columns), figsize=(15, 4))
    for axis, column in zip(axes, numeric_columns):
        axis.hist(sample[column].dropna(), bins=50, color="#4472C4")
        axis.set(title=f"{column} histogram", xlabel=column, ylabel="Line count")
    fig.tight_layout()
    fig.savefig(figure_dir / "univariate_numeric_histograms.png", dpi=150)
    plt.close(fig)
    saved.append("univariate_numeric_histograms.png")

    fig, axes = plt.subplots(1, len(numeric_columns), figsize=(12, 4))
    for axis, column in zip(axes, numeric_columns):
        axis.boxplot(sample[column].dropna(), orientation="vertical", showfliers=True)
        axis.set(title=f"{column} box plot", ylabel=column)
        axis.set_xticks([])
    fig.tight_layout()
    fig.savefig(figure_dir / "univariate_numeric_boxplots.png", dpi=150)
    plt.close(fig)
    saved.append("univariate_numeric_boxplots.png")

    for column, limit in (("Country", 15), ("StockCode", 20)):
        counts = sample[column].fillna("(missing)").value_counts().head(limit)
        if counts.empty:
            continue
        fig, axis = plt.subplots(figsize=(10, max(4, len(counts) * 0.28)))
        counts.sort_values().plot.barh(ax=axis, color="#70AD47")
        axis.set(
            title=f"Top {len(counts)} {column} categories by transaction-line count",
            xlabel="Line count",
            ylabel=column,
        )
        fig.tight_layout()
        filename = f"univariate_{column.casefold().replace(' ', '_')}_countplot.png"
        fig.savefig(figure_dir / filename, dpi=150)
        plt.close(fig)
        saved.append(filename)

    monthly = (
        sample.assign(month=sample["InvoiceDate"].dt.to_period("M").dt.to_timestamp())
        .groupby("month")["LineValue"]
        .sum()
    )
    fig, axis = plt.subplots(figsize=(10, 4))
    monthly.plot(ax=axis, color="#4472C4")
    axis.set(
        title="Monthly gross line value",
        xlabel="Invoice month",
        ylabel="Price times quantity",
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "monthly_gross_line_value.png", dpi=150)
    plt.close(fig)
    saved.append("monthly_gross_line_value.png")

    if sample["Country"].notna().any():
        countries = (
            sample.groupby("Country", dropna=False)["LineValue"]
            .sum()
            .nlargest(15)
            .sort_values()
        )
        fig, axis = plt.subplots(figsize=(9, 5))
        countries.plot.barh(ax=axis, color="#ED7D31")
        axis.set(
            title="Top countries by gross line value",
            xlabel="Price times quantity",
        )
        fig.tight_layout()
        fig.savefig(figure_dir / "top_countries_by_gross_line_value.png", dpi=150)
        plt.close(fig)
        saved.append("top_countries_by_gross_line_value.png")

    plotted = sample.sample(n=min(len(sample), 5000), random_state=42)
    fig, axis = plt.subplots(figsize=(7, 5))
    axis.scatter(plotted["Price"], plotted["Quantity"], alpha=0.25, s=10)
    axis.set(
        title="Unit price and quantity (random sample; descriptive only)",
        xlabel="Unit price",
        ylabel="Quantity",
    )
    fig.tight_layout()
    fig.savefig(figure_dir / "price_quantity_scatter.png", dpi=150)
    plt.close(fig)
    saved.append("price_quantity_scatter.png")

    correlation_columns = ("Price", "Quantity", "LineValue")
    if len(sample) >= 2:
        correlations = sample[list(correlation_columns)].corr(method="pearson")
        fig, axis = plt.subplots(figsize=(6, 5))
        image = axis.imshow(
            correlations.to_numpy(),
            cmap="coolwarm",
            vmin=-1,
            vmax=1,
            aspect="equal",
        )
        labels = list(correlations.columns)
        axis.set_xticks(range(len(labels)), labels=labels, rotation=45, ha="right")
        axis.set_yticks(range(len(labels)), labels=labels)
        for row in range(len(labels)):
            for column in range(len(labels)):
                value = correlations.iat[row, column]
                annotation = f"{value:.2f}" if pd.notna(value) else "N/A"
                axis.text(
                    column,
                    row,
                    annotation,
                    ha="center",
                    va="center",
                    color="black",
                )
        fig.colorbar(image, ax=axis, label="Pearson correlation")
        axis.set_title("Pearson correlations (descriptive only)")
        fig.tight_layout()
        fig.savefig(figure_dir / "numeric_correlation_heatmap.png", dpi=150)
        plt.close(fig)
        saved.append("numeric_correlation_heatmap.png")
        correlations.to_csv(figure_dir / "numeric_correlations.csv")
    return saved


def _write_eda_tables(sample: pd.DataFrame, output_dir: Path) -> None:
    sample[["Quantity", "Price", "LineValue"]].describe().T.to_csv(
        output_dir / "numeric_summary.csv"
    )

    missingness = pd.DataFrame(
        {
            "column": sample.columns,
            "missing_count": sample.isna().sum().to_numpy(),
            "missing_pct": (sample.isna().mean() * 100).to_numpy(),
        }
    )
    missingness.to_csv(output_dir / "analysis_sample_missingness.csv", index=False)

    categorical_rows: list[dict[str, Any]] = []
    for column in ("Country", "StockCode", "Description"):
        if column not in sample.columns:
            continue
        counts = sample[column].fillna("(missing)").value_counts().head(20)
        for value, count in counts.items():
            categorical_rows.append(
                {
                    "column": column,
                    "value": value,
                    "row_count": int(count),
                    "row_pct": float(count / len(sample) * 100) if len(sample) else 0.0,
                }
            )
    pd.DataFrame(
        categorical_rows, columns=("column", "value", "row_count", "row_pct")
    ).to_csv(output_dir / "top_categories.csv", index=False)

    outlier_rows: list[dict[str, float | int | str]] = []
    for column in ("Quantity", "Price"):
        q1 = float(sample[column].quantile(0.25))
        q3 = float(sample[column].quantile(0.75))
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        outlier_rows.append(
            {
                "column": column,
                "q1": q1,
                "q3": q3,
                "iqr_lower_bound": lower,
                "iqr_upper_bound": upper,
                "outside_iqr_count": int(
                    ((sample[column] < lower) | (sample[column] > upper)).sum()
                ),
            }
        )
    pd.DataFrame(outlier_rows).to_csv(output_dir / "iqr_outlier_review.csv", index=False)


def _missing_value_policy(column: str) -> str:
    canonical = COLUMN_ALIASES.get(_column_key(column), column)
    if canonical in REQUIRED_COLUMNS:
        return "Exclude rows missing this required field; do not impute"
    return "Retain missing values; do not impute or drop the column"


def _write_missing_value_audit(
    raw: pd.DataFrame,
    normalized: pd.DataFrame,
    sample: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Write per-column null counts at source, normalized, and analysis stages."""
    audit_rows: list[dict[str, Any]] = []

    def add_stage(frame: pd.DataFrame, stage: str) -> None:
        groups = (
            frame.groupby("source_sheet", dropna=False, sort=False)
            if "source_sheet" in frame.columns
            else [(stage, frame)]
        )
        for source_sheet, group in groups:
            for column in group.columns:
                if column == "source_sheet":
                    continue
                missing_count = int(group[column].isna().sum())
                audit_rows.append(
                    {
                        "stage": stage,
                        "source_sheet": source_sheet,
                        "column": column,
                        "missing_count": missing_count,
                        "missing_pct": (
                            float(missing_count / len(group) * 100)
                            if len(group)
                            else 0.0
                        ),
                        "policy": _missing_value_policy(str(column)),
                    }
                )

    add_stage(raw, "source")
    add_stage(normalized, "normalized")
    add_stage(sample, "analysis_sample")
    pd.DataFrame(
        audit_rows,
        columns=(
            "stage",
            "source_sheet",
            "column",
            "missing_count",
            "missing_pct",
            "policy",
        ),
    ).to_csv(output_dir / "missing_values.csv", index=False)


def _write_report(
    source_rows: int,
    normalized: pd.DataFrame,
    sample: pd.DataFrame,
    audit: pd.DataFrame,
    figures: list[str],
    output_dir: Path,
) -> None:
    date_min = sample["InvoiceDate"].min() if not sample.empty else pd.NaT
    date_max = sample["InvoiceDate"].max() if not sample.empty else pd.NaT
    date_range = (
        f"{date_min:%Y-%m-%d} to {date_max:%Y-%m-%d}"
        if pd.notna(date_min) and pd.notna(date_max)
        else "unavailable (no eligible rows)"
    )
    figure_links = (
        "\n".join(f"- `figures/{figure}`" for figure in figures)
        if figures
        else "- No figures generated because the analysis sample is empty."
    )
    quality_flags = (
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
    quality_lines = [
        f"- `{flag}`: {int(normalized[flag].sum()):,} rows "
        f"({normalized[flag].mean() * 100:.2f}%; flags may overlap)"
        for flag in quality_flags
        if flag in normalized.columns and normalized[flag].any()
    ]
    if not quality_lines:
        quality_lines = ["- No rows were flagged by the workflow's quality checks."]

    missing_columns = normalized.isna().sum()
    missing_findings = [
        f"- `{column}`: {int(count):,} missing "
        f"({count / len(normalized) * 100:.2f}%)"
        for column, count in missing_columns.items()
        if count and column != "source_sheet"
    ]
    if not missing_findings:
        missing_findings = ["- No missing values were found after normalization."]

    findings: list[str] = [
        f"- The analysis sample contains {len(sample):,} of {source_rows:,} "
        f"source rows ({len(sample) / source_rows * 100:.2f}% retained)"
        if source_rows
        else "- The source dataset contains no rows."
    ]
    if not sample.empty:
        for column in ("Price", "Quantity", "LineValue"):
            values = sample[column].dropna()
            if values.empty:
                continue
            findings.append(
                f"- `{column}` ranges from {values.min():,.4g} to "
                f"{values.max():,.4g}; median {values.median():,.4g}."
            )
        if len(sample) >= 2:
            price_quantity_corr = sample["Price"].corr(
                sample["Quantity"], method="pearson"
            )
            if pd.notna(price_quantity_corr):
                findings.append(
                    f"- Price and quantity have a Pearson correlation of "
                    f"{price_quantity_corr:.3f} in this analysis sample. This is "
                    "descriptive association, not a causal effect."
                )
            else:
                findings.append(
                    "- Price/quantity correlation is unavailable because at least "
                    "one variable has no variation."
                )
        else:
            findings.append(
                "- Pairwise correlations are unavailable with fewer than two "
                "analysis rows."
            )

        for column in ("Quantity", "Price"):
            q1, q3 = sample[column].quantile([0.25, 0.75])
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outlier_count = int(
                ((sample[column] < lower) | (sample[column] > upper)).sum()
            )
            findings.append(
                f"- `{column}` has {outlier_count:,} IQR-rule outlier(s) "
                f"(review bounds: {lower:,.4g} to {upper:,.4g}); "
                "review these observations rather than automatically removing them."
            )
        if sample["Country"].notna().any():
            top_country = sample["Country"].value_counts().index[0]
            top_country_count = int(sample["Country"].value_counts().iloc[0])
            findings.append(
                f"- The most frequent country is {top_country!s} "
                f"({top_country_count:,} transaction lines)."
            )
        if sample["StockCode"].notna().any():
            top_stock = sample["StockCode"].value_counts().index[0]
            top_stock_count = int(sample["StockCode"].value_counts().iloc[0])
            findings.append(
                f"- The most frequent stock code is {top_stock!s} "
                f"({top_stock_count:,} transaction lines); verify product/service "
                "scope before drawing conclusions."
            )
    else:
        findings.append(
            "- Distribution, correlation, and category findings are unavailable "
            "because no rows met the current analysis-sample rules."
        )

    report = f"""# Online Retail II preprocessing and EDA

## Dataset overview

- Input rows: {source_rows:,}
- Normalized rows retained, including flagged records: {len(normalized):,}
- Positive-sales analysis rows: {len(sample):,}
- Analysis date range: {date_range}
- Gross line value is calculated as `Quantity * Price`; it is not net revenue and
  does not account for discounts, taxes, shipping, or accounting adjustments.

## Reproducible row-selection audit

| Step | Rows removed | Rows remaining |
|---|---:|---:|
{chr(10).join(f"| {row.step} | {row.rows_removed:,} | {row.rows_remaining:,} |" for row in audit.itertuples(index=False))}

All source rows are retained in `normalized_transactions.csv`; excluded rows
remain inspectable with quality flags. The separate analysis sample excludes
exact duplicates after the first occurrence, cancellation invoices, rows with
missing or invalid core fields, non-positive quantities (including returns),
and non-positive prices. Duplicate removal is based on all normalized input
fields other than the workbook sheet label.

## Outputs

- `initial_inspection/`: per-source-sheet dimensions, `info()`, memory usage,
  head/tail samples, descriptive statistics, and original column-name audit.
- `deduplicated_transactions.csv`: normalized transaction rows with exact
  duplicates removed, retaining the first occurrence.
- `analysis_sample.csv`: analysis-ready positive-sales line items.
- `cleaning_audit.csv`: sequential, non-overlapping row attrition.
- `missing_values.csv`: per-column null counts and percentages at source,
  normalized, and analysis-sample stages, with the handling policy.
- `quality_issue_counts.csv`: counts for overlapping quality flags.
- `analysis_sample_missingness.csv`, `numeric_summary.csv`, `top_categories.csv`,
  and `iqr_outlier_review.csv`: descriptive tables. IQR observations are flagged
  for review, not automatically removed.
- `figures/numeric_correlations.csv` and
  `figures/numeric_correlation_heatmap.png`: Pearson correlations for price,
  quantity, and gross line value when at least two analysis rows are available.
- Univariate charts: histograms and box plots for price, quantity, and gross
  line value; count plots for the most frequent countries and stock codes.
  Box-plot fliers and IQR counts flag observations for investigation, not
  automatic removal.
- Bivariate/multivariate charts: a price-versus-quantity scatter plot and a
  Pearson correlation heatmap. Gross line value is defined from price and
  quantity, so its correlations with them are mechanically coupled and should
  not be interpreted as independent evidence.
- Figures:
{figure_links}

## Observed data-quality findings and descriptive insights

### Quality flags

{chr(10).join(quality_lines)}

### Missing-value profile

{chr(10).join(missing_findings)}

### Analysis-sample patterns

{chr(10).join(findings)}

These findings are calculated from the supplied dataset on each run.
Correlations and distribution summaries are descriptive only; they do not
establish causal effects. Review the cleaning rules and flagged records before
interpreting results.

## Interpretation cautions

- The positive-sales sample is a descriptive preprocessing choice, not a validated
  causal identification strategy. Review return and cancellation handling against
  the final research question.
- Stock codes for services, postage, adjustments, or non-product lines are not
  automatically removed. Inspect `top_categories.csv` and define product-scope
  rules explicitly if required.
- Missing customer IDs and descriptions are retained; missing core identifiers,
  dates, quantities, or prices prevent inclusion in the analysis sample.
- No values are imputed and no columns are dropped for missingness. Rows missing
  required transaction fields (`Invoice`, `StockCode`, `Quantity`, `InvoiceDate`,
  or `Price`) are excluded from the analysis sample, while optional descriptive
  fields remain missing. Mean/median imputation of price or quantity could
  distort the treatment or outcome; ID and date imputations would invent
  records, and categorical imputation would introduce unverified values.
  Consider imputation only for justified covariates after reviewing missingness
  patterns and documenting the method and its effect on causal estimates.
- Extreme observations are retained. Investigate them with domain knowledge
  before choosing any transformation or exclusion.
- Price may be endogenous to demand, promotions, and unobserved product or
  customer characteristics. EDA alone does not establish a causal price effect.
"""
    (output_dir / "eda_report.md").write_text(report, encoding="utf-8")


def run_workflow(
    input_path: str | Path,
    output_dir: str | Path = Path("data/processed/eda"),
    sheet_name: str | None = None,
) -> dict[str, int]:
    """Run loading, preprocessing, descriptive tables, plots, and report writing."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    raw = load_transactions(
        input_path,
        sheet_name=sheet_name,
        inspection_dir=destination,
    )
    normalized, sample, audit, issue_counts = prepare_transactions(raw)
    normalized.to_csv(destination / "normalized_transactions.csv", index=False)
    deduplicated = normalized.loc[~normalized["is_exact_duplicate"]].copy()
    deduplicated.to_csv(destination / "deduplicated_transactions.csv", index=False)
    sample.to_csv(destination / "analysis_sample.csv", index=False)
    audit.to_csv(destination / "cleaning_audit.csv", index=False)
    issue_counts.to_csv(destination / "quality_issue_counts.csv", index=False)
    _write_missing_value_audit(raw, normalized, sample, destination)
    _write_eda_tables(sample, destination)
    figures = _save_plots(sample, destination / "figures")
    _write_report(len(raw), normalized, sample, audit, figures, destination)
    return {"input_rows": len(raw), "analysis_rows": len(sample)}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preprocess and explore the provisional Online Retail II dataset."
    )
    parser.add_argument(
        "input_path", type=Path, help="Path to the downloaded CSV or Excel dataset."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/processed/eda"),
        help="Directory for tables, figures, and the generated report.",
    )
    parser.add_argument(
        "--sheet",
        help="Excel worksheet to read; omit to combine all worksheets. Ignored for CSV.",
    )
    arguments = parser.parse_args()
    result = run_workflow(
        arguments.input_path, arguments.output_dir, sheet_name=arguments.sheet
    )
    print(
        f"Preprocessing complete: {result['input_rows']:,} input rows; "
        f"{result['analysis_rows']:,} analysis rows. Outputs: {arguments.output_dir}"
    )


if __name__ == "__main__":
    main()

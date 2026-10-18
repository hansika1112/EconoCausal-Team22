import pandas as pd
import pytest

from src.data.retail_eda import (
    inspect_dataset,
    load_transactions,
    prepare_transactions,
    run_workflow,
)


@pytest.fixture
def retail_rows() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Invoice": ["10001", "10001", "C10002", "10003", "10004", "10005"],
            "StockCode": ["A1", "A1", "B2", "C3", "D4", "E5"],
            "Description": ["Widget", "Widget", "Return", "Returned item", "Free item", "Bad date"],
            "Quantity": [2, 2, 1, -1, 3, 1],
            "InvoiceDate": [
                "01/12/2010",
                "01/12/2010",
                "02/12/2010",
                "03/12/2010",
                "04/12/2010",
                "not-a-date",
            ],
            "Price": [5.0, 5.0, 4.0, 3.0, 0.0, 2.0],
            "Customer ID": [12345, 12345, 23456, 34567, 45678, 56789],
            "Country": ["UK", "UK", "France", "UK", "UK", "Germany"],
        }
    )


def test_prepare_transactions_retains_rows_and_audits_exclusions(
    retail_rows: pd.DataFrame,
) -> None:
    normalized, sample, audit, issue_counts = prepare_transactions(retail_rows)

    assert len(normalized) == 6
    assert len(sample) == 1
    assert sample.iloc[0]["Invoice"] == "10001"
    assert sample.iloc[0]["LineValue"] == 10.0
    assert audit["rows_remaining"].tolist() == [6, 5, 4, 3, 2, 1]
    assert issue_counts.set_index("issue").loc["is_return", "row_count"] == 1
    assert issue_counts.set_index("issue").loc["is_cancellation", "row_count"] == 1
    assert (
        issue_counts.set_index("issue").loc["invalid_invoice_date", "row_count"] == 1
    )


def test_prepare_transactions_rejects_missing_required_fields() -> None:
    with pytest.raises(ValueError, match="missing required Online Retail II columns"):
        prepare_transactions(pd.DataFrame({"Invoice": ["10001"]}))


def test_initial_inspection_reports_shape_info_samples_summary_and_column_issues() -> None:
    source = pd.DataFrame(
        {
            " Invoice ": ["10001", "10002"],
            "StockCode": ["A1", "A2"],
            "Quantity": [1, 2],
            "InvoiceDate": ["01/12/2010", "02/12/2010"],
            "Price": [5.0, 3.0],
        }
    )

    report, audit = inspect_dataset(source)

    assert "Dataset dimensions: 2 rows × 5 columns" in report
    assert "Memory usage (deep, including index):" in report
    assert "DataFrame.info():" in report
    assert "First five rows:" in report
    assert "Last five rows:" in report
    assert 'describe(include="all")' in report
    invoice_audit = audit.set_index("original_name").loc[" Invoice "]
    assert invoice_audit["canonical_name"] == "Invoice"
    assert "leading or trailing whitespace" in invoice_audit["format_issues"]
    assert "recognized alias for Invoice" in invoice_audit["format_issues"]


def test_run_workflow_writes_expected_outputs(
    retail_rows: pd.DataFrame, tmp_path
) -> None:
    source = tmp_path / "transactions.csv"
    retail_rows.to_csv(source, index=False)
    output_dir = tmp_path / "outputs"

    result = run_workflow(source, output_dir)

    assert result == {"input_rows": 6, "analysis_rows": 1}
    for filename in (
        "normalized_transactions.csv",
        "deduplicated_transactions.csv",
        "analysis_sample.csv",
        "cleaning_audit.csv",
        "missing_values.csv",
        "quality_issue_counts.csv",
        "analysis_sample_missingness.csv",
        "numeric_summary.csv",
        "top_categories.csv",
        "iqr_outlier_review.csv",
        "eda_report.md",
    ):
        assert (output_dir / filename).is_file()
    assert (output_dir / "initial_inspection" / "01_CSV.txt").is_file()
    assert (
        output_dir / "initial_inspection" / "column_format_audit.csv"
    ).is_file()
    assert (output_dir / "figures" / "price_quantity_scatter.png").is_file()
    for figure in (
        "univariate_numeric_histograms.png",
        "univariate_numeric_boxplots.png",
        "univariate_country_countplot.png",
        "univariate_stockcode_countplot.png",
    ):
        assert (output_dir / "figures" / figure).is_file()
    deduplicated = pd.read_csv(output_dir / "deduplicated_transactions.csv")
    assert len(deduplicated) == 5
    assert not deduplicated["is_exact_duplicate"].any()


def test_missing_value_audit_excludes_required_nulls_without_imputing_optional_fields(
    tmp_path,
) -> None:
    source = tmp_path / "missing_values.csv"
    pd.DataFrame(
        {
            "Invoice": ["10001", "10002"],
            "StockCode": ["A1", "A2"],
            "Description": [None, "Widget"],
            "Quantity": [2, 1],
            "InvoiceDate": ["01/12/2010", "02/12/2010"],
            "Price": [5.0, None],
            "Customer ID": [None, 12345],
            "Country": ["UK", "UK"],
        }
    ).to_csv(source, index=False)
    output_dir = tmp_path / "missing-output"

    result = run_workflow(source, output_dir)

    missing = pd.read_csv(output_dir / "missing_values.csv")
    source_price = missing.loc[
        (missing["stage"] == "source") & (missing["column"] == "Price")
    ].iloc[0]
    source_customer = missing.loc[
        (missing["stage"] == "source") & (missing["column"] == "Customer ID")
    ].iloc[0]
    analysis_customer = missing.loc[
        (missing["stage"] == "analysis_sample")
        & (missing["column"] == "Customer ID")
    ].iloc[0]

    assert result == {"input_rows": 2, "analysis_rows": 1}
    assert source_price["missing_count"] == 1
    assert "Exclude rows" in source_price["policy"]
    assert source_customer["missing_count"] == 1
    assert "Retain missing values" in source_customer["policy"]
    assert analysis_customer["missing_count"] == 1
    sample = pd.read_csv(output_dir / "analysis_sample.csv")
    assert pd.isna(sample.loc[0, "Customer ID"])
    report = (output_dir / "eda_report.md").read_text(encoding="utf-8")
    assert "### Missing-value profile" in report
    assert "`Customer ID`: 1 missing (50.00%)" in report
    assert "`Price` has 0 IQR-rule outlier(s) (review bounds:" in report


def test_workflow_writes_relationship_plots_and_observed_findings(tmp_path) -> None:
    source = tmp_path / "relationships.csv"
    pd.DataFrame(
        {
            "Invoice": ["10001", "10002", "10003"],
            "StockCode": ["A1", "A2", "A3"],
            "Quantity": [1, 2, 4],
            "InvoiceDate": ["01/12/2010", "02/12/2010", "03/12/2010"],
            "Price": [5.0, 3.0, 2.0],
            "Country": ["UK", "UK", "France"],
        }
    ).to_csv(source, index=False)
    output_dir = tmp_path / "relationship-output"

    run_workflow(source, output_dir)

    figures = output_dir / "figures"
    assert (figures / "price_quantity_scatter.png").is_file()
    assert (figures / "numeric_correlation_heatmap.png").is_file()
    correlations = pd.read_csv(figures / "numeric_correlations.csv", index_col=0)
    price_quantity_correlation = float(correlations.at["Price", "Quantity"])
    assert price_quantity_correlation < 0
    report = (output_dir / "eda_report.md").read_text(encoding="utf-8")
    assert "Observed data-quality findings and descriptive insights" in report
    assert "Pearson correlation" in report
    assert "most frequent country is UK (2 transaction lines)" in report
    assert "descriptive association, not a causal effect" in report


def test_load_workbook_combines_sheets_and_supports_sheet_selection(
    retail_rows: pd.DataFrame, tmp_path
) -> None:
    workbook = tmp_path / "transactions.xlsx"
    with pd.ExcelWriter(workbook) as writer:
        retail_rows.iloc[:2].to_excel(writer, sheet_name="First", index=False)
        retail_rows.iloc[2:4].to_excel(writer, sheet_name="Second", index=False)

    all_rows = load_transactions(workbook)
    first_sheet = load_transactions(workbook, sheet_name="First")

    assert len(all_rows) == 4
    assert set(all_rows["source_sheet"]) == {"First", "Second"}
    assert len(first_sheet) == 2
    assert set(first_sheet["source_sheet"]) == {"First"}


def test_run_workflow_handles_empty_analysis_sample(tmp_path) -> None:
    source = tmp_path / "cancellations.csv"
    pd.DataFrame(
        {
            "Invoice": ["C10001"],
            "StockCode": ["A1"],
            "Quantity": [1],
            "InvoiceDate": ["01/12/2010"],
            "Price": [5.0],
        }
    ).to_csv(source, index=False)
    output_dir = tmp_path / "empty-output"

    result = run_workflow(source, output_dir)

    assert result == {"input_rows": 1, "analysis_rows": 0}
    assert "no eligible rows" in (output_dir / "eda_report.md").read_text()
    assert list((output_dir / "figures").iterdir()) == []

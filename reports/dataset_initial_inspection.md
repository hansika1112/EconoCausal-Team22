# Dataset Initial Inspection Report

## 1. Project Information

- **Project:** EconoCausal: Dynamic Pricing via Double Machine Learning
- **Team:** Group 22
- **Dataset:** Online Retail II
- **Source:** UCI Machine Learning Repository
- **Dataset URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **Inspection Status:** Initial inspection completed
- **Model Training Status:** Not started

## 2. Dataset Overview

The Online Retail II dataset contains transactions from a UK-based online retail business covering December 2009 to December 2011.

| Property | Observed Value |
|---|---|
| Total data rows | 1,067,371 |
| Total columns | 8 |
| Worksheet 1 | Year 2009-2010 |
| Rows in Worksheet 1, including header | 525,462 |
| Worksheet 2 | Year 2010-2011 |
| Rows in Worksheet 2, including header | 541,911 |

### Columns

- Invoice
- StockCode
- Description
- Quantity
- InvoiceDate
- Price
- Customer ID
- Country

## 3. Data Quality Findings

The initial scan identified the following issues:

| Check | Count |
|---|---:|
| Missing Customer ID | 243,007 |
| Missing Description | 4,382 |
| Exact duplicate rows | 34,335 |
| Invoice values starting with `C` | 19,494 |
| Negative Quantity values | 22,950 |
| Zero Price values | 6,202 |
| Quantity greater than 1,000 | 352 |
| Price greater than 1,000 | 245 |
| Negative Price values | 5 |

The dataset contains mixed value types in some columns, including Invoice, StockCode, Description, and Price. These require further validation during preprocessing.

## 4. Initial Observations

1. Customer ID is missing in approximately 22.77% of the dataset.
2. Description is missing in approximately 0.41% of the dataset.
3. Exact duplicate rows account for approximately 3.22% of the dataset.
4. Invoice identifiers starting with `C` may indicate cancellations and require verification.
5. Negative quantities may represent returns or other adjustments.
6. High-quantity transactions may be legitimate bulk purchases. For example, some tissue products have recorded quantities above 4,000.
7. Zero and negative prices require investigation before deciding how they should be handled.
8. A Quantity threshold of greater than 1,000 identified 352 rows in this local scan. This count should be reconciled with other team members' results.

## 5. Proposed Preprocessing Approach

- Preserve the original raw dataset without modification.
- Investigate missing values and determine suitable handling rules.
- Verify cancellation invoices and negative-quantity transactions.
- Inspect exact duplicates before deciding whether to remove them.
- Flag transactions with Quantity greater than 1,000 rather than automatically deleting them.
- Investigate zero, negative, and unusually high prices.
- Compare analytical results with and without selected flagged observations as a sensitivity analysis.
- Document all preprocessing rules and the number of affected rows.

## 6. Relevance to Double Machine Learning

The proposed research question is:

**What is the average causal effect of product unit price on the quantity purchased in the Online Retail II dataset?**

The proposed treatment is Price, and the proposed outcome is Quantity. Potential control variables and the final analytical sample must be evaluated before model development.

Observed associations between price and quantity do not, by themselves, establish causality. Confounding, returns, cancellations, missing data, and the absence of explicit competitor-price or promotion indicators may limit causal interpretation.

## 7. Next Steps

1. Reconcile the high-quantity row count with the team's preprocessing results.
2. Investigate missing values, duplicates, cancellations, and unusual prices.
3. Define and document the analytical sample and preprocessing rules.
4. Conduct exploratory data analysis.
5. Finalize the treatment, outcome, controls, and identification assumptions.
6. Proceed to model development only after the dataset and methodology have been reviewed.

## 8. Limitations

This document records initial dataset inspection findings only. No trained model, estimated treatment effect, or empirical causal conclusion is reported at this stage.
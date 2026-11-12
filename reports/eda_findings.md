# Exploratory Data Analysis (EDA) Findings

## 1. Project Information

- **Project:** EconoCausal: Dynamic Pricing via Double Machine Learning
- **Team:** Group 22
- **Dataset:** Online Retail II
- **Source:** UCI Machine Learning Repository
- **Inspection status:** Initial EDA completed
- **Model training status:** Not started

## 2. Dataset Overview

The dataset contains 1,067,371 transaction rows across two worksheets covering December 2009 to December 2011.

| Property | Result |
|---|---:|
| Total rows | 1,067,371 |
| Total columns | 8 |
| Missing Customer ID | 243,007 |
| Missing Description | 4,382 |
| Combined exact duplicate rows | 34,335 |
| Invoice values starting with C | 19,494 |
| Negative Quantity rows | 22,950 |
| Zero Price rows | 6,202 |
| Quantity greater than 1,000 | 352 |
| Price greater than 1,000 | 245 |
| Negative Price rows | 5 |

## 3. Missing Values

### Customer ID

There are 243,007 rows with missing Customer ID, approximately 22.77% of the dataset.

**Proposed handling:** Do not automatically remove these rows. Assess whether they are useful for transaction-level price and quantity analysis.

### Description

There are 4,382 rows with missing Description, approximately 0.41% of the dataset.

**Proposed handling:** Inspect these records and determine whether StockCode or other available fields provide enough information for analysis.

## 4. Duplicate Transactions

The combined-dataset scan identified 34,335 exact duplicate rows, approximately 3.22% of the dataset.

The separate worksheet duplicate counts were:
- Year 2009-2010: 6,865
- Year 2010-2011: 5,268
- Sum of worksheet-level duplicate counts: 12,133

A cross-sheet comparison produced the following results:

| Check | Result |
|---|---:|
| Combined exact duplicate rows | 34,335 |
| Unique exact rows in Sheet 2 also found in Sheet 1 | 22,202 |
| Total matching rows returned by the cross-sheet merge | 22,523 |

The cross-sheet merge returned 22,523 matching rows, representing 22,202 unique exact rows. Repeated occurrences account for the difference between these two match counts. This supports the conclusion that exact records overlap across the worksheets and helps explain why the combined duplicate count exceeds the sum of worksheet-level counts.

The counts describe duplicate rows under exact matching across all eight columns. They do not establish that every repeated transaction is erroneous or should be removed.

**Proposed handling:** Preserve the raw data. Investigate repeated transactions and compare analysis results under clearly documented duplicate-handling strategies before removing any records.

## 5. Cancellations and Negative Quantities

- Invoice values starting with `C`: 19,494 rows.
- Negative Quantity values: 22,950 rows.

These counts are not identical. A cancellation indicator and a negative quantity should therefore be examined separately.

**Proposed handling:** Inspect cancellation invoices and negative-quantity transactions to understand returns and adjustments before defining the analytical sample.

## 6. Price and Quantity Checks

The initial scan found:
- 6,202 rows with Price equal to zero.
- 5 rows with negative Price.
- 245 rows with Price greater than 1,000.
- 352 rows with Quantity greater than 1,000.

Some high-quantity records appear to represent bulk purchases. Therefore, a high quantity alone is not sufficient evidence that a transaction is invalid.

**Proposed handling:**
1. Investigate zero and negative prices.
2. Review unusually high prices and quantities.
3. Flag unusual records rather than deleting them automatically.
4. Compare results with and without selected observations as a sensitivity analysis.

## 7. Relevance to Double Machine Learning

The proposed research question is:

**What is the average causal effect of product unit price on the quantity purchased in the Online Retail II dataset?**

- **Proposed treatment:** Price
- **Proposed outcome:** Quantity
- **Potential controls:** Product, time, and country-related features, subject to validation.

The research question, treatment, outcome, controls, and identification assumptions require further review before model training.

Observed associations between price and quantity do not, by themselves, establish causality. Potential confounding, returns, cancellations, missing data, and unavailable promotion or competitor-price indicators may limit causal interpretation.

## 8. Proposed Next Steps

1. Review the verified cross-sheet duplicate overlap and decide whether further record-level investigation is needed.
2. Examine missing values and unusual transactions.
3. Define transparent preprocessing rules.
4. Conduct price and quantity distribution analysis.
5. Review the proposed treatment, outcome, and control variables with the team.
6. Train and evaluate a DML estimator only after the analytical sample and methodology are agreed upon.

## 9. Limitations

This document reports initial data-quality findings only. No transaction rows have been deleted as part of this inspection, no model has been trained, and no empirical causal effect has been estimated.

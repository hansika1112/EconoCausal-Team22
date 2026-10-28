# DML Variable Selection — EconoCausal

## Project Objective
Estimate the causal effect of product price on sales quantity using
Double Machine Learning (DML), subject to suitable data and
identification assumptions.

## Candidate Variables

| Role | Candidate | Dataset column | Considerations |
|---|---|---|---|
| Treatment | Product price | Price | Numeric; inspect non-positive and unusual values |
| Outcome | Sales quantity | Quantity | Numeric; inspect returns, cancellations, and non-positive values |
| Potential confounder | Product identity | StockCode | May capture differences between products |
| Potential confounder | Country | Country | May capture differences across markets |
| Potential confounder | Time | InvoiceDate | Consider time trends and seasonality |
| Potential confounder | Customer identity | Customer ID | Missing for many records; assess suitability before use |

## Important Data Quality Checks

- The dataset contains 1,067,371 rows.
- Customer ID is missing in 243,007 rows.
- Quantity is non-positive in 22,950 rows.
- Price is non-positive in 6,207 rows.
- The dataset contains cancellation invoices; their treatment needs
  explicit consideration.
- Confirm whether Price is recorded at the transaction-line level and
  whether Quantity represents the intended sales outcome.

## Proposed Analysis Plan

1. Define the unit of analysis and the target causal question.
2. Decide how cancellations, returns, and non-positive values will be handled.
3. Inspect candidate confounders and missingness.
4. Establish a defensible causal identification strategy before model fitting.
5. Validate the final treatment, outcome, and confounder definitions.
6. Fit and evaluate a DML estimator only after these decisions are justified.

## Limitations

These variables are candidates, not a finalized causal specification.
This document does not establish that the proposed confounders are sufficient
to control confounding. No causal effect or model performance is claimed.

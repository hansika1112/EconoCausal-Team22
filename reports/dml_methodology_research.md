
# Double Machine Learning (DML) Research and Methodology

## Project

**Project Name:** EconoCausal: Dynamic Pricing via Double Machine Learning  
**Team Group:** 22  
**Assignment ID:** ITS/DSML/1192  
**Dataset:** Online Retail II

## 1. Research Objective

Investigate whether and how product unit price affects the quantity purchased, using Double Machine Learning (DML).

The final causal question must be confirmed after reviewing the dataset, the available confounders, and the mentor's guidance.

## 2. Dataset Overview

- **Dataset name:** Online Retail II
- **Repository:** UCI Machine Learning Repository
- **Dataset URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **License:** CC BY 4.0, as reported by the dataset collection team
- **Reported size:** 1,067,371 rows and 8 columns
- **Reported period:** 1 December 2009 to 9 December 2011

The reported columns are Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, and Country.

These details are based on the teammate's dataset update and must be checked against the downloaded data and official source before final analysis.

## 3. Core DML Concept

Double Machine Learning combines machine learning with causal inference to estimate a treatment effect while reducing sensitivity to errors in nuisance-model estimation.

The main components are:

- **Outcome model:** Estimates the outcome using observed controls.
- **Treatment model:** Estimates the treatment using observed controls.
- **Final estimation stage:** Uses residualized information and an appropriate estimator to estimate the treatment effect.

Cross-fitting can help reduce overfitting bias in nuisance-model predictions. DML does not automatically establish causality; its identification assumptions must be justified.

## 4. Tentative Variable Definitions

The following are proposed definitions, not final decisions.

- **Treatment (T):** Unit price (`Price`), subject to validation.
- **Outcome (Y):** Quantity (`Quantity`), subject to handling cancellations and returns.
- **Potential controls (W):** Product identifiers, time-related features, country, and other justified pre-treatment variables available in the dataset.
- **Potential effect modifiers (X):** Product category or other suitable observed characteristics, if supported by the data.

The exact variables, transformations, and causal question must be confirmed after dataset inspection and mentor guidance.

## 5. Data Quality and Preprocessing Risks

The dataset collection update reported the following issues:

- Missing Customer ID values and a small number of missing Description values.
- Duplicate rows.
- Cancellation invoices and negative quantities associated with returns.
- Zero, negative, or extreme prices.
- Non-product codes representing fees, postage, and adjustments.
- Extreme quantity and price observations.

These observations have not yet been independently verified.

Proposed checks:

1. Inspect column names, data types, and missing-value counts.
2. Investigate duplicate records before deciding whether to remove them.
3. Identify cancellations, returns, and non-product transactions.
4. Validate zero, negative, and extreme prices.
5. Document each cleaning rule and quantify how many records it affects.
6. Preserve a reproducible record of the raw data and preprocessing steps.

Cleaning rules must be justified by the business question; records should not be removed solely to obtain convenient model results.

## 6. Proposed DML Workflow

1. Verify the official dataset source, license, and downloaded data.
2. Review the dataset structure and EDA findings.
3. Define the causal question and candidate treatment and outcome.
4. Identify plausible pre-treatment confounders and assess their availability.
5. Evaluate whether treatment variation and adequate overlap are present.
6. Establish an appropriate baseline.
7. Select a suitable DML estimator and nuisance learners.
8. Apply an appropriate data-splitting and cross-fitting strategy.
9. Estimate treatment effects and uncertainty where identification assumptions permit.
10. Evaluate robustness, document limitations, and report findings.

## 7. Assumptions and Risks

- Relevant confounders must be observed and appropriately controlled.
- There must be sufficient treatment variation and overlap.
- Variable timing and the causal question must be specified correctly.
- Post-treatment variables must not be included as ordinary controls without justification.
- Price may be influenced by demand, promotions, or other factors not recorded in the dataset.
- Returns, cancellations, and repeated transactions may affect the interpretation of quantity.
- The dataset does not appear to include competitor-price or promotion indicators in the reported column list.
- Causal conclusions must not be claimed unless the identification assumptions are defensible.

## 8. Evaluation Plan

After the dataset and estimator are confirmed:

- Evaluate nuisance-model predictions with suitable metrics.
- Report the treatment-effect estimate and confidence interval where supported.
- Check overlap and relevant diagnostics.
- Conduct robustness or sensitivity checks where feasible.
- Compare against a suitable baseline.
- Report limitations and avoid interpreting predictive performance as proof of causality.

## 9. Pending Decisions

- Verify the dataset and license against the official source.
- Review Duppada's dataset documentation and preprocessing notebook.
- Review Kumbha's EDA findings.
- Confirm the exact causal question with the team and mentor.
- Finalize treatment, outcome, and justified controls.
- Select the appropriate DML estimator and nuisance learners.
- Confirm the evaluation requirements.

## Status

Research draft updated using the dataset details reported by the collection team. The raw data, cleaning decisions, and EDA findings still require review. No dataset-specific model has been trained, and no empirical results are claimed.

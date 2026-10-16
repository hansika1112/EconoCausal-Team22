# Double Machine Learning (DML) Research and Methodology

## Project Information

- **Project Name:** EconoCausal: Dynamic Pricing via Double Machine Learning
- **Team Group:** 22
- **Organization:** Infotact Solutions Internship
- **Assignment ID:** ITS/DSML/1192
- **Dataset:** Online Retail II

## 1. Research Objective

The objective of this project is to investigate whether and how product unit price affects the quantity purchased using Double Machine Learning (DML).

The project aims to estimate the causal effect of pricing decisions while accounting for relevant observed factors that may influence both price and purchasing behavior.

The final causal question will be confirmed after reviewing the dataset, available confounders, exploratory data analysis (EDA), and mentor guidance.

### Proposed Primary Research Question

**What is the average causal effect of product unit price on the quantity purchased in the Online Retail II dataset?**

This is a provisional research question. Its feasibility depends on the available data, defensible identification assumptions, and the mentor's approval.

## 2. Dataset Overview

- **Dataset Name:** Online Retail II
- **Repository:** UCI Machine Learning Repository
- **Dataset URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **License:** CC BY 4.0, as reported by the dataset collection team
- **Reported Size:** 1,067,371 rows and 8 columns
- **Reported Period:** 1 December 2009 to 9 December 2011

The reported columns are Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, and Country.

These details are based on the dataset collection team's update and must be verified against the official source and downloaded data before final analysis.

## 3. Core DML Concept

Double Machine Learning combines machine learning with causal inference to estimate treatment effects while reducing sensitivity to errors in nuisance-model estimation.

The main components are:

- **Outcome Model:** Estimates the outcome using observed control variables.
- **Treatment Model:** Estimates the treatment using observed control variables.
- **Final Estimation Stage:** Uses residualized information and an appropriate estimator to estimate the treatment effect.
- **Cross-Fitting:** Uses separate data folds for nuisance-model training and prediction to help reduce overfitting bias.

DML does not automatically establish causality. The assumptions required to identify the causal effect must be justified using the dataset and domain knowledge.

## 4. Proposed Research Question and Variable Definitions

The following definitions are tentative and must be validated after dataset inspection.

### 4.1 Treatment (T)

Product unit price, represented by the reported `Price` column.

The treatment definition must account for zero, negative, and extreme price values and determine whether the observed price variation is appropriate for the research question.

### 4.2 Outcome (Y)

Quantity purchased per invoice line, represented by the reported `Quantity` column.

Negative quantities and cancellation transactions must be investigated before defining the final analysis population.

### 4.3 Potential Controls (W)

Potential controls may include product identifiers, time-related features, country, and other observed variables that plausibly influence both pricing and purchasing behavior.

Controls must be selected based on their causal relevance and timing. Variables should not be included merely because they improve prediction.

### 4.4 Potential Effect Modifiers (X)

Product category or other observed characteristics may be considered to investigate whether price effects differ across groups, provided the data supports such analysis.

Heterogeneous treatment effects are a possible extension. The initial focus is the average treatment effect, if it can be identified under defensible assumptions.

## 5. Data Quality and Preprocessing Risks

The dataset collection update reported the following potential issues:

- Missing Customer ID values and some missing Description values.
- Duplicate rows.
- Cancellation invoices and negative quantities associated with returns.
- Zero, negative, or extreme prices.
- Non-product codes representing fees, postage, and adjustments.
- Extreme quantity and price observations.

These observations have not yet been independently verified.

### Proposed Data Validation and Cleaning Workflow

1. Inspect column names, data types, row counts, and missing-value counts.
2. Investigate duplicate records before deciding whether to remove them.
3. Identify cancellations, returns, and non-product transactions.
4. Validate zero, negative, and extreme prices.
5. Examine quantity and price distributions and investigate outliers.
6. Document each cleaning decision and quantify its effect on the dataset.
7. Preserve the raw data and make preprocessing reproducible.
8. Coordinate the final cleaning rules with the EDA findings and research objective.

Cleaning decisions must be justified by the business question. Records should not be removed solely to obtain convenient model results.

## 6. Proposed DML Workflow

1. Verify the official dataset source, license, and downloaded data.
2. Review the dataset documentation and EDA findings.
3. Define the causal question and candidate treatment and outcome.
4. Identify plausible pre-treatment confounders and assess their availability.
5. Evaluate treatment variation and overlap.
6. Define the analysis population and document exclusion rules.
7. Establish an appropriate baseline model.
8. Select a suitable DML estimator and nuisance learners.
9. Apply an appropriate data-splitting and cross-fitting strategy.
10. Estimate treatment effects and uncertainty where identification assumptions permit.
11. Evaluate relevant diagnostics and robustness.
12. Document findings, limitations, and reproducibility details.

### 6.1 EDA Findings and DML Readiness

The dataset inspection and cleaning notebook was executed locally, and its validation and reload checks passed. The documented cleaning workflow retained 1,003,340 rows from the original 1,067,371 transaction rows (94.0%).

Key findings relevant to the proposed DML analysis include:

- Customer ID is missing for 22.6% of the cleaned transaction rows.
- The cleaning workflow removes duplicate records, cancellation invoices, non-positive quantities, non-positive prices, and identified non-product stock codes.
- Quantity and price outliers are flagged rather than automatically removed in the current configuration.
- The cleaned transaction data contains 196,242 product-week rows across 4,724 products and 104 weeks in the reported aggregation.
- The dataset does not provide explicit competitor-price or promotion indicators, which limits the ability to account for all potential price–quantity confounding.

These findings are descriptive and do not establish a causal price effect.

### 6.2 Proposed Analysis Readiness Checks

Before fitting a DML estimator:

1. Confirm the final treatment, outcome, analysis unit, and target estimand with the team and mentor.
2. Verify that product-week aggregation preserves meaningful price and quantity variation.
3. Inspect the distribution of price and quantity and document the treatment of returns and cancellations.
4. Select candidate controls based on causal relevance and timing, not prediction accuracy alone.
5. Assess treatment overlap and the availability of comparable observations.
6. Define a reproducible data-splitting strategy that accounts for the repeated product and time structure where appropriate.
7. Establish a baseline and sensitivity checks before interpreting any estimated treatment effect.

No DML model has been fitted as part of this update, and no causal estimate is claimed.

## 7. Assumptions and Risks

The following issues must be assessed before making causal claims:

- **Confounding:** Relevant common causes of price and quantity must be observed and appropriately controlled.
- **Treatment Variation:** Sufficient variation and overlap must exist across relevant observations.
- **Correct Specification:** The causal question, variable timing, and analysis population must be clearly defined.
- **Control Selection:** Post-treatment variables must not be used as ordinary controls without justification.
- **Price Endogeneity:** Price may be influenced by demand, promotions, product characteristics, or other factors not recorded in the dataset.
- **Returns and Cancellations:** Negative quantities and cancellation records may change the interpretation of the outcome.
- **Repeated Transactions:** Multiple transactions for the same product or customer may affect dependence assumptions and validation design.
- **Unobserved Factors:** The reported column list does not include explicit competitor-price or promotion indicators. Other unobserved confounders may also remain.

If relevant confounding cannot be adequately addressed, results must be described as associations or estimates under explicit assumptions rather than definitive causal effects.

## 8. Estimator Selection

The final estimator has not yet been selected.

The choice between an appropriate DML estimator and other causal methods will depend on:

- Whether price is treated as a continuous treatment.
- The structure and variation of the treatment.
- The outcome definition and distribution.
- The available controls and identification assumptions.
- The mentor's requirements and the feasibility of diagnostic checks.

A specialized dynamic DML estimator should not be selected solely because the project title contains the word “Dynamic.” The estimator must match the actual causal question and data structure.

## 9. Evaluation Plan

After the dataset, analysis population, and estimator are confirmed:

- Evaluate nuisance-model predictions using suitable metrics.
- Report the treatment-effect estimate and confidence interval where supported.
- Check treatment overlap and relevant diagnostics.
- Conduct robustness or sensitivity checks where feasible.
- Compare with an appropriate baseline.
- Document data exclusions, assumptions, and limitations.
- Distinguish predictive performance from causal identification.

No evaluation metrics or treatment-effect results will be reported until the analysis has been performed.

## 10. Team Coordination and Pending Decisions

The following items remain pending:

- Verify the dataset and license against the official source.
- Review the dataset documentation and preprocessing notebook from Duppada.
- Review Kumbha's EDA findings.
- Confirm the final causal question with the team and mentor.
- Finalize treatment, outcome, and justified controls.
- Select the appropriate estimator and nuisance learners.
- Confirm the validation strategy and evaluation requirements.
- Document the final methodology and limitations.

## 11. References

1. UCI Machine Learning Repository. *Online Retail II*. https://archive.ics.uci.edu/dataset/502/online+retail+ii
2. EconML Documentation. *Double Machine Learning*. https://econml.azurewebsites.net/spec/estimation/dml.html
3. DoubleML Documentation. *Basics of Double Machine Learning*. https://docs.doubleml.org/stable/guide/basics.html

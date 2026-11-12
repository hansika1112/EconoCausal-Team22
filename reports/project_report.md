# EconoCausal: Dynamic Pricing via Double Machine Learning

**Team Group:** 22  
**Organization:** Infotact Solutions Internship  
**Assignment ID:** ITS/DSML/1192  
**Project Type:** Data Science and Machine Learning

---

## 1. Problem Statement

Pricing decisions influence product demand and business revenue. Understanding the relationship between product prices and quantities sold is important for developing informed pricing strategies.

However, historical retail data is observational. Prices may be influenced by product characteristics, geographic markets, purchasing patterns, promotions, and other factors that also affect demand.

EconoCausal investigates the relationship between product prices and quantities sold using Double Machine Learning (DML), with the objective of estimating price-related effects while accounting for selected observable confounders.

## 2. Objectives

- Analyze historical retail transaction data.
- Perform data cleaning and exploratory data analysis.
- Identify relevant treatment, outcome, and confounding variables.
- Implement a Double Machine Learning estimation pipeline.
- Evaluate outcome and treatment nuisance models.
- Conduct preliminary sample-stability analysis.
- Present findings, assumptions, and limitations transparently.

## 3. Dataset and Data Source

**Dataset:** Online Retail II

**Data source and license:** The dataset is identified as Online Retail II. The original download URL, attribution requirements, and license should be confirmed and documented before final submission.

**Processed dataset dimensions:**
- Rows: 1,003,340
- Columns: 19
- Unique invoices: 39,516
- Unique products: 4,724
- Unique customers with recorded IDs: 5,852
- Countries: 43
- Time period: December 2009 to December 2011

The processed dataset contains transaction-level retail information, including product identifiers, quantities, prices, invoice dates, countries, and engineered analytical features.

## 4. Data Preprocessing

The preprocessing workflow includes:

- Removing duplicate records.
- Excluding cancellation invoices.
- Removing non-positive quantities.
- Removing non-positive prices.
- Excluding non-product stock codes.
- Retaining positive-sales observations.
- Creating revenue, log-price, and log-quantity features.
- Creating time-based features such as week and month.
- Identifying quantity and price outliers using flags rather than automatically removing them.
- Retaining missing customer identifiers and creating a known-customer indicator.

**Important data observations:**

- Missing Customer IDs: 226,761 (approximately 22.6%).
- Quantity outliers are flagged rather than removed.
- Price outliers are flagged rather than removed.
- No missing values remain in the processed analytical columns.
- The model preparation stage additionally validates required features and removes invalid observations.

The resulting dataset represents cleaned positive product sales. It does not include the excluded cancellation, return, and non-product records.

## 5. Exploratory Data Analysis

The initial dataset analysis identified:

- 1,003,340 processed transaction rows.
- 39,516 unique invoices.
- 4,724 unique products.
- 43 countries.
- 25 distinct months.
- Price variation across 4,249 products.
- Multiple prices within product-month groups, indicating observable price variation.

Missing customer identifiers vary across countries and months. This is an important data-quality consideration when interpreting customer-level purchasing behavior.

The analysis also identified quantity and price outliers. These observations were retained with corresponding flags to avoid unnecessary information loss.

Detailed EDA findings are documented in:
- `reports/eda_findings.md`
- `reports/dataset_initial_inspection.md`
- `reports/price_quantity_analysis.md`

## 6. Methodology

### 6.1 Causal Question

What is the relationship between product price and quantity sold, after accounting for the selected observable product, country, and time characteristics?

### 6.2 Treatment Variable

`log_price`

Represents the logarithm of product price.

### 6.3 Outcome Variable

`log_quantity`

Represents the logarithm of quantity sold.

### 6.4 Selected Confounders

- `StockCode`: Product identifier.
- `Country`: Geographic market.
- `month`: Monthly time indicator.

These are the currently selected observable controls. Their inclusion does not guarantee that all relevant confounding factors have been addressed.

### 6.5 DML Estimator

The project uses EconML's `LinearDML` estimator with continuous treatment.

The nuisance models use:
- OneHotEncoder for categorical features.
- Ridge regression for prediction.
- Three-fold GroupKFold cross-fitting.
- Invoice identifiers as grouping variables.

Invoice-group-aware cross-fitting prevents records belonging to the same invoice from being split across training and validation folds.

The final model uses no effect modifiers (X=None), so it estimates a constant treatment effect rather than heterogeneous effects across products or countries.

### 6.6 Identification Assumptions and Limitations

A causal interpretation requires assumptions including:

- No important unobserved confounding after conditioning on selected controls.
- Adequate treatment variation and overlap.
- Appropriate nuisance-model specification.
- Correct treatment and outcome definitions.

Potential unobserved factors include promotions, inventory availability, customer purchasing decisions, bulk discounts, and demand shocks.

GroupKFold cross-fitting does not automatically provide invoice-clustered standard errors. The reported confidence intervals should therefore not be described as invoice-cluster-adjusted.

## 7. Evaluation and Results

### 7.1 Pilot Model

The initial technical pilot used 250 invoices.

- Observations: 6,152
- Estimated coefficient: -0.585
- Standard error: 0.017
- Reported 95% confidence interval: [-0.617, -0.553]

### 7.2 Main Pilot

The larger pilot used 1,500 invoices.

- Observations: 37,296
- Products: 3,630
- Countries: 19
- Months: 25
- Estimated coefficient: -0.788
- Standard error: 0.010
- Reported 95% confidence interval: [-0.807, -0.769]

The estimated coefficient is negative, indicating an inverse relationship between log price and log quantity in this fitted observational model.

The estimate is not, by itself, proof of a causal price elasticity.

### 7.3 Nuisance Model Diagnostics

Mean cross-fitting R-squared scores from the 1,500-invoice pilot:

| Model | Mean R-squared |
|---|---:|
| Outcome model (log_quantity) | 0.1398 |
| Treatment model (log_price) | 0.5547 |

The outcome model has relatively limited predictive performance. Additional pre-treatment predictors and alternative nuisance-model specifications should be investigated.

### 7.4 Preliminary Robustness Analysis

Three separate samples of 500 invoices were evaluated.

| Random seed | Observations | Estimated effect | Standard error |
|---|---:|---:|---:|
| 21 | 13,051 | -0.7382 | 0.0127 |
| 42 | 10,988 | -0.6412 | 0.0127 |
| 84 | 12,319 | -0.6939 | 0.0130 |

All three estimates are negative, although their magnitudes differ.

This provides preliminary evidence of directional consistency across the selected samples. It does not establish causal robustness or eliminate sample sensitivity.

### 7.5 Generated Evaluation Reports

- `reports/dml_pilot_summary.json`
- `reports/dml_diagnostics.json`
- `reports/dml_diagnostics.md`
- `reports/dml_robustness.json`

## 8. Conclusion and Limitations

EconoCausal implements a Double Machine Learning pipeline to investigate the relationship between product prices and quantities sold using historical retail transaction data.

The project includes:
- Data preprocessing and feature engineering.
- Exploratory data analysis.
- A continuous-treatment EconML LinearDML estimator.
- Invoice-group-aware cross-fitting.
- Nuisance-model diagnostics.
- Preliminary robustness testing across different invoice samples.
- Automated tests for core data preparation and diagnostic functionality.

The estimated price coefficient is consistently negative across the three preliminary robustness samples. However, its magnitude varies, and the outcome nuisance model has relatively low predictive performance.

Further work is required before making causal or business-pricing recommendations. Important next steps include investigating additional confounders, assessing treatment overlap, improving nuisance-model specifications, evaluating inference that accounts for invoice-level dependence, and testing alternative model specifications.

The current findings should be interpreted as preliminary observational estimates rather than established causal effects.

## 9. References

The following references should be completed and verified before final submission:

1. Online Retail II dataset: original publisher, download URL, and license.
2. Chernozhukov et al.: Double/Debiased Machine Learning for Treatment and Structural Parameters.
3. EconML documentation: LinearDML estimator and inference.
4. Scikit-learn documentation: GroupKFold, OneHotEncoder, and Ridge regression.
5. Pandas documentation: data preparation and transformation.


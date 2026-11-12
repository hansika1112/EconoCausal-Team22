# Preprocessing Sensitivity Analysis

## 1. Project Information

- **Project:** EconoCausal: Dynamic Pricing via Double Machine Learning
- **Dataset:** Online Retail II
- **Total original rows:** 1,067,371
- **Analysis type:** Comparison of alternative preprocessing scenarios
- **Raw dataset modified:** No
- **Model training status:** Not started

## 2. Scenario Comparison

| Scenario | Rows retained | Rows excluded | Retained (%) | Quantity mean | Price mean |
|---|---:|---:|---:|---:|---:|
| Original dataset | 1,067,371 | 0 | 100.00% | 9.9389 | 4.6494 |
| Exclude cancellation invoices | 1,047,877 | 19,494 | 98.17% | 10.5924 | 3.9011 |
| Exclude negative quantities | 1,044,421 | 22,950 | 97.85% | 11.1761 | 3.9144 |
| Exclude nonpositive prices | 1,061,164 | 6,207 | 99.42% | 10.2994 | 4.8261 |
| Positive quantity and price | 1,041,671 | 25,700 | 97.59% | 10.9634 | 4.0770 |
| Positive, non-cancellation sales | 1,041,670 | 25,701 | 97.59% | 10.9635 | 4.0767 |

## 3. Median Comparison

Across all six scenarios:

- Quantity median: 3
- Price median: 2.10

The means change between scenarios, while the medians remain unchanged. This suggests that the filtering rules affect the average values more noticeably than the median values in this dataset.

## 4. Key Observations

1. Excluding cancellation invoices removes 19,494 rows and changes the Quantity mean from 9.9389 to 10.5924.
2. Excluding negative quantities removes 22,950 rows and increases the Quantity mean to 11.1761.
3. Excluding zero and negative prices removes 6,207 rows and changes the Price mean from 4.6494 to 4.8261.
4. The positive-quantity-and-price scenario retains 1,041,671 rows, or 97.59% of the original dataset.
5. Excluding cancellation invoices in addition to requiring positive Quantity and Price removes one additional row in the current comparison.

These are descriptive findings. They do not establish which scenario is best for causal estimation.

## 5. Interpretation and Limitations

- Cancellation invoices and negative quantities are not equivalent categories; their handling requires investigation.
- Zero-price transactions may have legitimate explanations and should not automatically be considered invalid.
- Large quantities and unusual prices require transaction-level review.
- The comparison uses simple row filters. It does not yet establish a valid causal identification strategy.
- The overlap between filtering rules should be examined at the record level before finalizing the analytical sample.

## 6. Proposed Next Steps

1. Review the scenarios with the team.
2. Investigate the meaning of cancellation invoices, returns, and zero-price records.
3. Define the target population and analytical sample before training a model.
4. Document the rationale for each selected rule.
5. Re-run descriptive statistics after the team approves the preprocessing approach.
6. Finalize treatment, outcome, controls, and causal assumptions before DML estimation.

## 7. Status

This report compares possible preprocessing choices only. No rows were deleted from the original dataset, no preprocessing scenario has been selected as final, no model has been trained, and no causal effect has been estimated.

# Price and Quantity Distribution Analysis

## 1. Overview

- Dataset: Online Retail II
- Total rows analyzed: 1,067,371
- Analysis type: Descriptive statistics and extreme-value inspection
- Raw dataset modified: No

## 2. Distribution Statistics

| Statistic | Quantity | Price |
|---|---:|---:|
| Mean | 9.9389 | 4.6494 |
| Median | 3 | 2.10 |
| Minimum | -80,995 | -53,594.36 |
| Maximum | 80,995 | 38,970 |
| 1st percentile | -3 | 0.21 |
| 5th percentile | 1 | 0.42 |
| 25th percentile | 1 | 1.25 |
| 75th percentile | 10 | 4.15 |
| 95th percentile | 30 | 9.95 |
| 99th percentile | 100 | 18 |
| Skewness | 3.9961 | -69.1647 |

The Quantity distribution is positively skewed. The Price distribution has extreme negative values that strongly affect its skewness. These statistics describe the raw data and do not establish causal effects.

## 3. Extreme-Value Inspection

### Negative prices

The first worksheet contains negative prices for records described as `Adjust bad debt`, including values of -53,594.36, -44,031.79, and -38,925.87.

The second worksheet also contains negative `Adjust bad debt` records, including -11,062.06.

These records require separate investigation before deciding whether they belong in the product-price treatment variable.

### Large quantities

The first worksheet includes large quantities for products such as mugs and paper cups, including orders of 19,152 and 12,960 units.

The second worksheet includes a quantity of 80,995 for `PAPER CRAFT, LITTLE BIRDIE` and a matching negative quantity of -80,995 on a cancellation invoice.

High quantities may represent bulk orders or cancellations. Quantity magnitude alone is not sufficient evidence for deleting a record.

### Zero-price records

Zero-price records appear in both worksheets. Some records also have missing descriptions.

These records should be investigated to understand whether they represent free items, adjustments, incomplete records, or another transaction type.

## 4. Proposed Handling

1. Preserve the raw dataset.
2. Investigate bad-debt adjustment records separately from ordinary product sales.
3. Identify cancellation and return transactions using multiple fields, not invoice prefix alone.
4. Flag extreme quantities and prices for review.
5. Compare analytical results under documented sample definitions.
6. Do not remove observations solely because they are extreme.

## 5. Relevance to Double Machine Learning

The proposed treatment is unit Price and the proposed outcome is Quantity. Before fitting a DML estimator, the team must define how to handle non-product adjustments, cancellations, returns, and zero-price records.

The choice of analytical sample can affect the estimated treatment effect. Any conclusions must acknowledge potential confounding and the limitations of the available data.

## 6. Status

This is a descriptive analysis only. No records were deleted, no DML model was trained, and no causal effect was estimated.

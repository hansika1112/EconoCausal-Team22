# Dataset: Online Retail II

## Overview

| Item | Details |
|---|---|
| **Name** | Online Retail II |
| **Source** | UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/502/online+retail+ii |
| **DOI** | https://doi.org/10.24432/C5CG6D |
| **License** | CC BY 4.0 (credit the source when using or sharing) |
| **Creator** | Daqing Chen (donated 2019) |
| **Description** | All transactions of a UK-based, non-store online retailer that mainly sells gift-ware. Many customers are wholesalers. |
| **Period** | 01 Dec 2009 to 09 Dec 2011 |
| **Size** | 1,067,371 rows x 8 columns |
| **File** | `online_retail_II.xlsx` (about 43.5 MB), two sheets: `Year 2009-2010` (525,461 rows) and `Year 2010-2011` (541,910 rows) |

**Citation:** Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

## Getting the data

The raw file is **not committed** to this repository because of its size. Download it from the source link above and place it in `data/raw/`. This folder is listed in `.gitignore`.

```python
import pandas as pd

xl = pd.ExcelFile("data/raw/online_retail_II.xlsx")
df = pd.concat(
    [xl.parse(sheet) for sheet in xl.sheet_names],
    ignore_index=True,
)
```

Alternatively, with the `ucimlrepo` package: `fetch_ucirepo(id=502)`.

## Columns

Column names below are as they appear in the Excel file. The UCI web page uses slightly different names (InvoiceNo, UnitPrice, CustomerID).

| Column | Type | Description | Role in our DML setup |
|---|---|---|---|
| `Invoice` | text | Invoice number. A prefix "C" marks a cancellation. | Identifier, used to filter returns |
| `StockCode` | text | Product code | Confounder (product) |
| `Description` | text | Product name | Optional, text features |
| `Quantity` | integer | Units per product per transaction | **Outcome** (log-transformed) |
| `InvoiceDate` | datetime | Date and time of the transaction | Confounder (time, seasonality) |
| `Price` | float | Unit price in GBP | **Treatment** (log-transformed) |
| `Customer ID` | float | Customer number | Mostly missing, optional flag |
| `Country` | text | Customer's country | Confounder |

## Summary statistics

- Unique products: 5,305 as stored (5,131 after standardising letter case in `StockCode`)
- Unique customers: 5,942 (excluding missing IDs)
- Unique invoices: 53,628
- Countries: 43 (United Kingdom is about 91.9% of rows)

## Data quality findings (raw data, each issue counted independently)

Categories overlap, so counts should not be added together.

| Issue | Rows | Share of rows |
|---|---|---|
| Missing `Customer ID` | 243,007 | 22.8% |
| Missing `Description` | 4,382 | 0.4% |
| Fully duplicated rows | 34,335 | 3.2% |
| Cancellation invoices (prefix "C") | 19,494 | 1.8% |
| Negative `Quantity` | 22,950 | 2.2% |
| Zero `Price` | 6,202 | 0.6% |
| Negative `Price` | 5 | <0.01% |
| Non-product stock codes (POST, DOT, M, D, S, C2, BANK CHARGES, ADJUST, AMAZONFEE, PADS, CRUK, TEST, GIFT_ vouchers) | 5,930 | 0.6% |
| `Quantity` above 1,000 (max is 80,995) | 352 | 0.03% |
| `Price` above 100 (max is 38,970 in the raw data) | 1,946 | 0.18% |

## Cleaning rules and rows affected

Rules run in the order below, so "rows matching" counts rows that meet the rule at that step. Every rule and threshold is configurable in the configuration cell of `notebooks/01_dataset_inspection_and_cleaning.ipynb`.

| Rule | Default | Rows matching | Rows removed |
|---|---|---|---|
| Duplicate rows | remove | 34,335 | 34,335 |
| Cancellation invoices | remove | 19,104 | 19,104 |
| `Quantity` <= 0 | remove | 3,393 | 3,393 |
| `Price` <= 0 | remove | 2,626 | 2,626 |
| Non-product stock codes | remove | 4,573 | 4,573 |
| `Quantity` above 1,000 (`quantity_outlier`) | **flag only** | 299 | 0 |
| Price outliers (`price_outlier`) | **flag only** | 3,328 | 0 |

**Result:** 1,003,340 rows (94.0% of the raw data) remain, including the flagged rows.

Price outliers combine two flags: `price_high_abs` (price above 100, 187 rows) and `price_ratio_outlier` (price more than 5x above or below the product's own median, 3,149 rows). A few rows meet both.

`Customer ID` is not imputed. It is kept as is, with a `known_customer` flag.

### Flagged quantity outliers (299 rows)
- 158 invoices, 155 products, and 61 known customers.
- 8.3% of all units but only 2.9% of revenue, because they are mostly low-priced items (median price 0.25 versus 2.10 overall).
- Mostly UK (216 rows), then Denmark (41) and France (25). Only 2% have no Customer ID, compared with 22.6% overall.
- A few invoices contribute many lines (two invoices have 25 flagged lines each).

### Flagged unusual prices
- Genuine high-value products: 13 products have prices above 100, mostly furniture such as vintage kitchen cabinets and sideboards.
- Suspicious values: some low-cost products have very high one-off prices that look like entry errors. For example, `FLAG OF ST GEORGE CAR FLAG` has a median price of 0.42 but lines up to 1,157.15, and `PICNIC BASKET WICKER 60 PIECES` has a median of 5.95 but a line at 649.50.
- The highest prices in the cleaned data are therefore **not all furniture**. The notebook (section 7) lists these cases with each product's typical price.

### Preliminary sensitivity (descriptive only, not the DML estimate)
A simple within-product regression of log weekly quantity on log weekly average price gives a slope of about -1.39 with all rows, -1.37 without quantity outliers, -1.51 without price outliers, and -1.50 without both. This ignores confounding and is only meant to show how sensitive a simple estimate is to the flagged rows.

## Suitability for Double Machine Learning

**Strengths**
- Contains a treatment (`Price`), an outcome (`Quantity`), and observable confounders (time, product, country).
- Large enough for flexible ML models of the nuisance functions.
- About 90% of products (89.9%) have more than one line-level price over the period, and among products with at least 20 weeks of data, 99.1% have more than one weekly price level.
- Caution: the median within-product variation of weekly average price is about 24%, which is high. Weekly averages mix wholesale and retail lines, so part of this may be order mix and not real price changes. This needs to be verified in EDA.

**Limitations**
- **No promotion or competitor-price columns.** Promotions that coincide with price changes are an unobserved confounder, which can bias elasticity estimates.
- **Prices are not randomized.** Variation may reflect wholesale versus retail pricing or product lifecycle rather than deliberate pricing decisions.
- **Quantity is not the same as demand.** No stock or availability data, so low quantity can reflect stockouts.
- **Wholesale customers** create very large orders that distort the quantity distribution.
- **Single retailer, UK-centric.** Results may not generalize to other markets.
- **Customer ID is missing for about a quarter of rows**, which limits customer-level analysis.

## Suggested preparation for modelling

1. Clean using the rules above (implemented in the cleaning notebook; the cleaned file, with flag columns, is saved to `data/processed/` and not committed). Compare results with and without the flagged rows before fixing any cutoff.
2. Aggregate to product-week level (average price, total quantity).
3. Use log(price) and log(quantity) so the treatment effect reads as price elasticity.
4. Build confounders: product, week, month, holiday season, lagged sales, country share.
5. Check overlap (enough price variation within each product) before fitting.
6. State the missing-promotion limitation in the final report.

*Prepared by Duppada Dhanalakshmi for Issue #1 (Dataset Collection).*

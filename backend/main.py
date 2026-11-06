from pathlib import Path
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "processed" / "online_retail_clean.csv.gz"

app = FastAPI(
    title="EconoCausal API",
    description="Dataset analytics API for the EconoCausal dashboard",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def load_dataset():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_csv(DATA_FILE, compression="gzip")

    required = [
        "Invoice", "Quantity", "Price", "revenue",
        "month", "StockCode", "Description",
        "Customer ID", "quantity_outlier", "price_outlier",
    ]

    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")

    return df


@app.get("/")
def home():
    return {
        "message": "EconoCausal API is running",
        "docs": "/docs",
    }


@app.get("/api/overview")
def overview():
    df = load_dataset()

    return {
        "total_rows": int(len(df)),
        "total_columns": int(len(df.columns)),
        "total_transactions": int(df["Invoice"].nunique()),
        "total_revenue": round(float(df["revenue"].sum()), 2),
        "average_price": round(float(df["Price"].mean()), 2),
        "total_quantity": int(df["Quantity"].sum()),
        "missing_customer_ids": int(df["Customer ID"].isna().sum()),
    }


@app.get("/api/dataset-health")
def dataset_health():
    df = load_dataset()
    total = len(df)

    missing_customer = int(df["Customer ID"].isna().sum())
    quantity_outliers = int(df["quantity_outlier"].sum())
    price_outliers = int(df["price_outlier"].sum())

    return {
        "total_rows": total,
        "missing_customer_ids": missing_customer,
        "missing_customer_percentage": round(
            missing_customer / total * 100, 2
        ) if total else 0,
        "quantity_outlier_count": quantity_outliers,
        "quantity_outlier_percentage": round(
            quantity_outliers / total * 100, 2
        ) if total else 0,
        "price_outlier_count": price_outliers,
        "price_outlier_percentage": round(
            price_outliers / total * 100, 2
        ) if total else 0,
    }


@app.get("/api/monthly-trends")
def monthly_trends():
    df = load_dataset()

    monthly = (
        df.groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            demand=("Quantity", "sum"),
        )
        .sort_values("month")
    )

    return monthly.to_dict(orient="records")


@app.get("/api/price-demand")
def price_demand():
    df = load_dataset()

    products = (
        df.groupby("Description", as_index=False)
        .agg(
            price=("Price", "mean"),
            demand=("Quantity", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values("revenue", ascending=False)
        .head(5)
    )

    products["price"] = products["price"].round(2)
    products["demand"] = products["demand"].astype(int)
    products["revenue"] = products["revenue"].round(2)

    return products.to_dict(orient="records")

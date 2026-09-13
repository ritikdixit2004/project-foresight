"""
Project FORESIGHT — Data Pipeline
"""
import pandas as pd
import numpy as np
import os

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

def load_raw():
    sales = pd.read_csv(f"{RAW_DIR}/sales_daily.csv")
    sku = pd.read_csv(f"{RAW_DIR}/sku_master.csv")
    cal = pd.read_csv(f"{RAW_DIR}/calendar.csv")
    inv = pd.read_csv(f"{RAW_DIR}/inventory_snapshots.csv")
    return sales, sku, cal, inv

def clean_sales(sales):
    sales = sales.copy()
    sales["Date"] = pd.to_datetime(sales["Date"])
    sales = sales.drop_duplicates(subset=["Date", "SKU"])
    sales = sales[(sales["Units_Sold"] >= 0) & (sales["Revenue"] >= 0)]
    sales = sales.rename(columns={
        "Date": "date", "SKU": "sku_id", "Units_Sold": "units_sold",
        "Revenue": "revenue", "Price": "unit_price", "Promotion": "promo_flag"
    })
    return sales

def clean_sku_master(sku):
    sku = sku.copy()
    sku["Launch_Date"] = pd.to_datetime(sku["Launch_Date"])
    sku = sku.drop_duplicates(subset=["SKU"])
    sku = sku.rename(columns={
        "SKU": "sku_id", "Product_Name": "product_name", "Category": "category",
        "Subcategory": "subcategory", "Launch_Date": "launch_date",
        "Cost_Price": "unit_cost", "Selling_Price": "list_price",
        "Gross_Margin_Per_Unit": "gross_margin_per_unit"
    })
    sku["is_loss_making"] = sku["gross_margin_per_unit"] < 0
    return sku

def clean_calendar(cal):
    cal = cal.copy()
    cal["date"] = pd.to_datetime(cal["date"])
    cal = cal.drop_duplicates(subset=["date"])
    cal["holiday"] = cal["holiday"].fillna("None")
    cal["promotion_event"] = cal["promotion_event"].fillna("None")
    return cal

def clean_inventory(inv):
    inv = inv.copy()
    inv["Snapshot_Date"] = pd.to_datetime(inv["Snapshot_Date"])
    inv = inv.drop_duplicates(subset=["Snapshot_Date", "SKU"])
    inv = inv.rename(columns={
        "Snapshot_Date": "date", "SKU": "sku_id", "Current_Stock": "on_hand_units",
        "On_Order": "on_order_units", "Lead_Time_Days": "lead_time_days",
        "Safety_Stock": "safety_stock", "Reorder_Point": "reorder_point",
        "Inventory_Value": "inventory_value"
    })
    return inv

def build_master_dataset(sales, sku, cal):
    df = sales.merge(sku, on="sku_id", how="left")
    df = df.merge(cal, on="date", how="left")
    return df

def run_pipeline():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    sales_raw, sku_raw, cal_raw, inv_raw = load_raw()

    sales = clean_sales(sales_raw)
    sku = clean_sku_master(sku_raw)
    cal = clean_calendar(cal_raw)
    inv = clean_inventory(inv_raw)

    skus_with_sales = set(sku["sku_id"])
    inv["has_sales_history"] = inv["sku_id"].isin(skus_with_sales)

    master = build_master_dataset(sales, sku, cal)

    master.to_csv(f"{PROCESSED_DIR}/master_sales.csv", index=False)
    inv.to_csv(f"{PROCESSED_DIR}/inventory_clean.csv", index=False)
    sku.to_csv(f"{PROCESSED_DIR}/sku_master_clean.csv", index=False)

    print(f"master_sales.csv: {master.shape}")
    print(f"inventory_clean.csv: {inv.shape}")
    print(f"sku_master_clean.csv: {sku.shape}")
    print(f"SKUs with sales history: {len(skus_with_sales)} / {inv['sku_id'].nunique()} in inventory")
    print(f"Loss-making SKUs flagged: {sku['is_loss_making'].sum()}")

if __name__ == "__main__":
    run_pipeline()
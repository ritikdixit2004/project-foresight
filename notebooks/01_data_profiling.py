"""
Project FORESIGHT — Data Profiling

"""
import pandas as pd

sales = pd.read_csv('data/raw/sales_daily.csv')
sku = pd.read_csv('data/raw/sku_master.csv')
cal = pd.read_csv('data/raw/calendar.csv')
inv = pd.read_csv('data/raw/inventory_snapshots.csv')

print("="*60)
print("CHECK 1: MISSING VALUES")
print("="*60)
for name, df in [('sales_daily', sales), ('sku_master', sku), ('calendar', cal), ('inventory_snapshots', inv)]:
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print(f"\n{name}:")
        print(missing)
    else:
        print(f"\n{name}: koi missing value nahi")

print("\n" + "="*60)
print("CHECK 2: DUPLICATE ROWS")
print("="*60)
for name, df in [('sales_daily', sales), ('sku_master', sku), ('calendar', cal), ('inventory_snapshots', inv)]:
    print(f"{name}: {df.duplicated().sum()} duplicate rows")

print("\n" + "="*60)
print("CHECK 3: SKU CONSISTENCY ACROSS FILES")
print("="*60)
sku_in_master = set(sku['SKU'])
sku_in_sales = set(sales['SKU'])
sku_in_inv = set(inv['SKU'])
print(f"sku_master mein SKUs: {len(sku_in_master)}")
print(f"sales_daily mein SKUs: {len(sku_in_sales)}")
print(f"inventory mein SKUs: {len(sku_in_inv)}")
print(f"Inventory mein extra SKUs jo master/sales mein nahi hain: {len(sku_in_inv - sku_in_master)}")

print("\n" + "="*60)
print("CHECK 4: INVALID / WEIRD VALUES")
print("="*60)
print(f"Negative units_sold: {(sales['Units_Sold'] < 0).sum()}")
print(f"Negative/zero price: {(sales['Price'] <= 0).sum()}")
print(f"Loss-making SKUs (cost > selling price): {(sku['Gross_Margin_Per_Unit'] < 0).sum()}")
print(f"Negative stock in inventory: {(inv['Current_Stock'] < 0).sum()}")

print("\n" + "="*60)
print("CHECK 5: DATE RANGE & CONTINUITY")
print("="*60)
sales['Date'] = pd.to_datetime(sales['Date'])
print(f"Sales data date range: {sales['Date'].min().date()} to {sales['Date'].max().date()}")
days_per_sku = sales.groupby('SKU')['Date'].nunique()
print(f"Har SKU ke liye din count — min: {days_per_sku.min()}, max: {days_per_sku.max()} (731 hona chahiye)")
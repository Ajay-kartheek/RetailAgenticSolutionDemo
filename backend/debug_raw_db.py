#!/usr/bin/env python3
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from shared.db import DynamoDBClient
from config.settings import settings

db = DynamoDBClient()

print("="*60)
print("Checking raw DB data for PROD_WS001 @ STORE_CHN")
print("="*60)

# Check inventory
all_inv = db.scan(settings.inventory_table)
ws_inv = [i for i in all_inv if i.get('product_id') == 'PROD_WS001' and i.get('store_id') == 'STORE_CHN']
print(f"\nInventory records: {len(ws_inv)}")
for inv in ws_inv:
    print(f"  Stock: {inv.get('quantity')} | Safety: {inv.get('safety_stock')} | Status: {inv.get('stock_status')}")

# Check forecast
all_fc = db.scan(settings.demand_forecast_table)
ws_fc = [f for f in all_fc if f.get('product_id') == 'PROD_WS001' and f.get('store_id') == 'STORE_CHN']
print(f"\nForecast records: {len(ws_fc)}")
for fc in ws_fc:
    print(f"  Demand: {fc.get('forecasted_demand')} | Confidence: {fc.get('confidence')} | Period: {fc.get('forecast_period')}")

# Check sales
all_sales = db.scan(settings.sales_table)
ws_sales = [s for s in all_sales if s.get('product_id') == 'PROD_WS001' and s.get('store_id') == 'STORE_CHN']
print(f"\nSales records: {len(ws_sales)}")
total_sold = sum(s.get('quantity_sold', 0) for s in ws_sales)
print(f"  Total sold: {total_sold}")

# Calculate the ratio
if ws_inv and ws_fc:
    stock = ws_inv[0].get('quantity', 0)
    demand = ws_fc[0].get('forecasted_demand', 0)
    remaining_demand = max(0, demand - total_sold)
    ratio = stock / remaining_demand if remaining_demand > 0 else 999
    print(f"\n>>> Calculated ratio: {stock} / {remaining_demand} = {ratio:.4f}")
    print(f">>> Is understocked (ratio < 0.7)? {'YES' if ratio < 0.7 else 'NO'}")
else:
    print("\n>>> Missing inventory or forecast data!")

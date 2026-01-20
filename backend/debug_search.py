
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.absolute()))

from backend.agents.inventory_agent.tools import search_inventory_items
import json
from decimal import Decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

print("Searching for understocked items (ratio < 0.7)...")
result = search_inventory_items(max_stock_ratio=0.7, forecast_period="2026-Q1", limit=200)

items = result.get('items', [])
print(f"Found {len(items)} understocked items.\n")

# Sort by ratio ascending (most critical first)
items.sort(key=lambda x: x.get('stock_to_demand_ratio', 99))

# Find Wool Blend Sweater at Chennai
found = False
for idx, item in enumerate(items):
    pid = item.get('product_id')
    store = item.get('store_id')
    ratio = item.get('stock_to_demand_ratio')
    
    if pid == 'PROD_WS001' and store == 'STORE_CHN':
        print(f"✅ FOUND PROD_WS001 at STORE_CHN at position {idx+1}:")
        print(json.dumps(item, cls=DecimalEncoder, indent=2))
        found = True
        break

if not found:
    print("❌ PROD_WS001 at STORE_CHN NOT found in understocked items.")
    # Print top 10 for context
    print("\nTop 10 most critical items:")
    for i, item in enumerate(items[:10]):
        pid = item.get('product_id')
        store = item.get('store_id')
        ratio = item.get('stock_to_demand_ratio')
        print(f"  {i+1}. {pid} @ {store} - ratio={ratio}")
    
    # Check if WS001 for Chennai exists in ANY items
    ws001_chennai = [i for i in items if i.get('product_id') == 'PROD_WS001' and i.get('store_id') == 'STORE_CHN']
    if not ws001_chennai:
        print("\n PROD_WS001@STORE_CHN was NOT in the search results at all. Checking raw data...")
        # Manually query the DB
        from backend.shared.db import DynamoDBClient
        from backend.config.settings import settings
        
        db = DynamoDBClient()
        all_fc = db.scan(settings.demand_forecast_table)
        ws_fc = [f for f in all_fc if f.get('product_id') == 'PROD_WS001' and f.get('store_id') == 'STORE_CHN']
        print(f"  Forecast for PROD_WS001@STORE_CHN: {ws_fc}")
        
        all_inv = db.scan(settings.inventory_table)
        ws_inv = [i for i in all_inv if i.get('product_id') == 'PROD_WS001' and i.get('store_id') == 'STORE_CHN']
        print(f"  Inventory for PROD_WS001@STORE_CHN: {ws_inv}")

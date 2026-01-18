#!/usr/bin/env python3
"""
Demo Data Seeder for SK Brands Retail AI Platform
=================================================
Creates controlled demo scenarios for showcase demonstrations.
Uses existing stores from sk_stores table.

Usage:
    python demo_seeder.py --scenario 1   # Winter stock crisis scenario
    python demo_seeder.py --scenario 2   # Spring sales opportunity scenario
    python demo_seeder.py --clear        # Clear all demo data
"""

import argparse
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent to path for imports
sys.path.insert(0, '.')

from config.aws import get_dynamodb_resource
from config.settings import settings

dynamodb = get_dynamodb_resource()

# ============================================================================
# PRODUCT DATA (Same for both scenarios)
# ============================================================================
PRODUCTS = [
    {"product_id": "PROD_WS001", "name": "Wool Blend Sweater", "category": "Winterwear", "cost": 600, "price": 1799, "sku_base": "WS001"},
    {"product_id": "PROD_LJ002", "name": "Lightweight Jacket", "category": "Outerwear", "cost": 800, "price": 2499, "sku_base": "LJ002"},
    {"product_id": "PROD_CK003", "name": "Cotton Kurta", "category": "Traditional", "cost": 300, "price": 999, "sku_base": "CK003"},
    {"product_id": "PROD_DJ004", "name": "Denim Jeans", "category": "Bottomwear", "cost": 450, "price": 1499, "sku_base": "DJ004"},
]

# ============================================================================
# SCENARIO 1: Winter Stock Crisis
# Distributed across ALL stores
# ============================================================================
SCENARIO_1 = {
    "name": "Winter Stock Crisis",
    "description": "Peak winter season causing stock volatility across all stores",
    "store_configs": {
        # Major stores with specific issues
        "STORE_CHN": {"ws": 5, "lj": 45, "ck": 80, "dj": 35, "issue": "CRITICAL_LOW_SWEATERS"},
        "STORE_BLR": {"ws": 120, "lj": 60, "ck": 200, "dj": 55, "issue": "OVERSTOCKED_KURTAS"},
        "STORE_HYD": {"ws": 200, "lj": 150, "ck": 100, "dj": 80, "issue": "WELL_STOCKED_DONOR"},
        "STORE_KCH": {"ws": 60, "lj": 5, "ck": 70, "dj": 50, "issue": "CRITICAL_LOW_JACKETS"},
        "STORE_CBE": {"ws": 40, "lj": 35, "ck": 30, "dj": 0, "issue": "OUT_OF_STOCK_JEANS"},
        "STORE_VZG": {"ws": 80, "lj": 70, "ck": 60, "dj": 120, "issue": "OVERSTOCKED_JEANS_DONOR"},
        "STORE_MDU": {"ws": 40, "lj": 8, "ck": 65, "dj": 45, "issue": "LOW_JACKETS"},
        "STORE_MYS": {"ws": 50, "lj": 40, "ck": 12, "dj": 40, "issue": "LOW_KURTAS"},
        
        # Other stores - balanced or minor issues
        "STORE_TVM": {"ws": 50, "lj": 35, "ck": 50, "dj": 40},
        "STORE_TRC": {"ws": 45, "lj": 30, "ck": 55, "dj": 38},
        "STORE_SLM": {"ws": 55, "lj": 42, "ck": 48, "dj": 45},
        "STORE_ERD": {"ws": 48, "lj": 38, "ck": 52, "dj": 42},
        "STORE_TPR": {"ws": 52, "lj": 45, "ck": 60, "dj": 48},
        "STORE_TJV": {"ws": 46, "lj": 36, "ck": 54, "dj": 44},
        "STORE_VLR": {"ws": 50, "lj": 40, "ck": 50, "dj": 46},
        "STORE_NGL": {"ws": 48, "lj": 38, "ck": 52, "dj": 42},
        "STORE_TCH": {"ws": 44, "lj": 34, "ck": 48, "dj": 40},
    },
    "sales": [
        # High demand patterns
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 25, "days_ago": 1},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 22, "days_ago": 2},
        {"store_id": "STORE_KCH", "product_id": "PROD_LJ002", "quantity": 18, "days_ago": 1},
        {"store_id": "STORE_KCH", "product_id": "PROD_LJ002", "quantity": 20, "days_ago": 2},
        {"store_id": "STORE_HYD", "product_id": "PROD_WS001", "quantity": 30, "days_ago": 1},
        
        # Slow moving
        {"store_id": "STORE_BLR", "product_id": "PROD_CK003", "quantity": 2, "days_ago": 1},
    ],
    "forecasts": [
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "forecasted_demand": 150, "confidence": 0.92},
        {"store_id": "STORE_CBE", "product_id": "PROD_DJ004", "forecasted_demand": 120, "confidence": 0.89},
        {"store_id": "STORE_KCH", "product_id": "PROD_LJ002", "forecasted_demand": 100, "confidence": 0.91},
        {"store_id": "STORE_BLR", "product_id": "PROD_CK003", "forecasted_demand": 40, "confidence": 0.75},
        {"store_id": "STORE_HYD", "product_id": "PROD_WS001", "forecasted_demand": 180, "confidence": 0.88},
    ],
}

# ============================================================================
# SCENARIO 2: Spring Sales Opportunity
# ============================================================================
SCENARIO_2 = {
    "name": "Spring Sales Opportunity",
    "description": "Transition to spring, clearing winter stock across all regions",
    "store_configs": {
        # Spring clearance patterns
        "STORE_CHN": {"ws": 85, "lj": 70, "ck": 50, "dj": 40, "issue": "WINTER_CLEARANCE"},
        "STORE_BLR": {"ws": 60, "lj": 55, "ck": 45, "dj": 38},
        "STORE_VZG": {"ws": 40, "lj": 35, "ck": 60, "dj": 15, "issue": "HIGH_DENIM_DEMAND"},
        "STORE_HYD": {"ws": 70, "lj": 60, "ck": 150, "dj": 80, "issue": "NEW_COLLECTION_PREP"},
        "STORE_KCH": {"ws": 55, "lj": 40, "ck": 65, "dj": 50},
        "STORE_MDU": {"ws": 45, "lj": 40, "ck": 55, "dj": 30},
        "STORE_CBE": {"ws": 50, "lj": 45, "ck": 60, "dj": 42},
        "STORE_MYS": {"ws": 48, "lj": 42, "ck": 40, "dj": 38},
        
        # Rest balanced
        "STORE_TVM": {"ws": 52, "lj": 38, "ck": 58, "dj": 44},
        "STORE_TRC": {"ws": 46, "lj": 36, "ck": 52, "dj": 38},
        "STORE_SLM": {"ws": 50, "lj": 40, "ck": 55, "dj": 45},
        "STORE_ERD": {"ws": 48, "lj": 38, "ck": 50, "dj": 42},
        "STORE_TPR": {"ws": 52, "lj": 42, "ck": 58, "dj": 46},
        "STORE_TJV": {"ws": 46, "lj": 36, "ck": 52, "dj": 40},
        "STORE_VLR": {"ws": 50, "lj": 40, "ck": 54, "dj": 44},
        "STORE_NGL": {"ws": 48, "lj": 38, "ck": 50, "dj": 42},
        "STORE_TCH": {"ws": 44, "lj": 34, "ck": 48, "dj": 38},
    },
    "sales": [
        {"store_id": "STORE_VZG", "product_id": "PROD_DJ004", "quantity": 18, "days_ago": 1},
        {"store_id": "STORE_VZG", "product_id": "PROD_DJ004", "quantity": 22, "days_ago": 2},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "quantity": 2, "days_ago": 1},
        {"store_id": "STORE_HYD", "product_id": "PROD_CK003", "quantity": 20, "days_ago": 1},
    ],
    "forecasts": [
        {"store_id": "STORE_VZG", "product_id": "PROD_DJ004", "forecasted_demand": 150, "confidence": 0.94},
        {"store_id": "STORE_CHN", "product_id": "PROD_WS001", "forecasted_demand": 15, "confidence": 0.80},
        {"store_id": "STORE_HYD", "product_id": "PROD_CK003", "forecasted_demand": 200, "confidence": 0.92},
    ],
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_existing_stores():
    """Fetch all stores from sk_stores table."""
    table = dynamodb.Table(settings.stores_table)
    response = table.scan()
    return response.get('Items', [])

def clear_table(table_name: str):
    """Delete all items from a table."""
    try:
        table = dynamodb.Table(table_name)
        scan = table.scan()
        items = scan.get("Items", [])
        
        key_names = [k["AttributeName"] for k in table.key_schema]
        
        with table.batch_writer() as batch:
            for item in items:
                key = {k: item[k] for k in key_names if k in item}
                batch.delete_item(Key=key)
        
        print(f"  ✓ Cleared {len(items)} items from {table_name}")
    except Exception as e:
        print(f"  ✗ Error clearing {table_name}: {e}")

def put_item(table_name: str, item: dict):
    """Put an item into a table."""
    table = dynamodb.Table(table_name)
    serialized = {}
    for k, v in item.items():
        if isinstance(v, float):
            serialized[k] = Decimal(str(v))
        else:
            serialized[k] = v
    table.put_item(Item=serialized)

def seed_products():
    """Seed product data."""
    print("\n🏷️  Seeding products...")
    for product in PRODUCTS:
        put_item(settings.products_table, product)
    print(f"  ✓ Added {len(PRODUCTS)} products")

def seed_transfer_routes(stores):
    """Generate transfer routes between major hubs."""
    print("\n🚚 Seeding transfer routes...")
    
    # Define hub stores
    hubs = ["STORE_CHN", "STORE_BLR", "STORE_HYD", "STORE_KCH", "STORE_VZG"]
    
    routes = []
    for hub in hubs:
        for store in stores:
            if store["store_id"] != hub and store["store_id"] in [s["store_id"] for s in stores]:
                # Add route from hub to store
                routes.append({
                    "route_id": f"{hub}#{store['store_id']}",
                    "from_store_id": hub,
                    "to_store_id": store["store_id"],
                    "transit_days": 1 if store["store_id"] in hubs else 2,
                    "cost_per_unit": 15 if store["store_id"] in hubs else 25,
                    "is_active": True,
                })
    
    # Add routes for first 50 to avoid too many
    for route in routes[:50]:
        put_item(settings.store_transfers_table, route)
    
    print(f"  ✓ Added {min(len(routes), 50)} routes")

def seed_inventory(scenario: dict, stores):
    """Seed inventory for ALL stores."""
    print("\n📦 Seeding inventory...")
    count = 0
    
    product_keys = {"ws": "PROD_WS001", "lj": "PROD_LJ002", "ck": "PROD_CK003", "dj": "PROD_DJ004"}
    
    for store in stores:
        store_id = store["store_id"]
        config = scenario["store_configs"].get(store_id, {"ws": 50, "lj": 40, "ck": 50, "dj": 45})
        
        for key, product_id in product_keys.items():
            product = next((p for p in PRODUCTS if p["product_id"] == product_id), None)
            if not product:
                continue
            
            quantity = config.get(key, 50)
            item = {
                "store_id": store_id,
                "sku": f"{product['sku_base']}#M#DEFAULT",
                "product_id": product_id,
                "quantity": quantity,
                "safety_stock": 40 if quantity < 40 else 30,
                "reorder_point": 25 if quantity < 25 else 20,
                "last_updated": datetime.utcnow().isoformat(),
            }
            put_item(settings.inventory_table, item)
            count += 1
    
    print(f"  ✓ Added {count} inventory records")

def seed_sales(scenario: dict):
    """Seed sales data."""
    print("\n💰 Seeding sales data...")
    count = 0
    for sale in scenario["sales"]:
        sale_date = (datetime.utcnow() - timedelta(days=sale["days_ago"])).strftime("%Y-%m-%d")
        product = next((p for p in PRODUCTS if p["product_id"] == sale["product_id"]), None)
        if not product:
            continue
        
        item = {
            "store_product_id": f"{sale['store_id']}#{sale['product_id']}",
            "sale_date": sale_date,
            "store_id": sale["store_id"],
            "product_id": sale["product_id"],
            "quantity_sold": sale["quantity"],
            "revenue": sale["quantity"] * product["price"],
            "unit_price": product["price"],
        }
        put_item(settings.sales_table, item)
        count += 1
    print(f"  ✓ Added {count} sales records")

def seed_forecasts(scenario: dict):
    """Seed ML demand forecasts."""
    print("\n📊 Seeding demand forecasts...")
    forecast_period = "2026-Q1"
    for fc in scenario["forecasts"]:
        product = next((p for p in PRODUCTS if p["product_id"] == fc["product_id"]), None)
        if not product:
            continue
        
        item = {
            "product_store_id": f"{fc['product_id']}#{fc['store_id']}",
            "forecast_period": forecast_period,
            "store_id": fc["store_id"],
            "product_id": fc["product_id"],
            "product_name": product["name"],
            "forecasted_demand": fc["forecasted_demand"],
            "confidence": fc["confidence"],
            "model_version": "demo-v1",
            "generated_at": datetime.utcnow().isoformat(),
        }
        put_item(settings.demand_forecast_table, item)
    print(f"  ✓ Added {len(scenario['forecasts'])} forecasts")

def clear_all_data():
    """Clear demo tables."""
    print("\n🗑️  Clearing existing data...")
    tables = [
        settings.inventory_table,
        settings.sales_table,
        settings.demand_forecast_table,
        settings.decisions_table,
        settings.agent_activity_table,
    ]
    for table in tables:
        clear_table(table)

def seed_scenario(scenario_num: int):
    """Seed a specific demo scenario."""
    scenario = SCENARIO_1 if scenario_num == 1 else SCENARIO_2
    
    print(f"\n{'='*60}")
    print(f"🎬 DEMO SCENARIO {scenario_num}: {scenario['name']}")
    print(f"   {scenario['description']}")
    print(f"{'='*60}")
    
    # Get existing stores
    stores = get_existing_stores()
    print(f"\n📍 Found {len(stores)} stores in database")
    
    # Clear existing data
    clear_all_data()
    
    # Seed data
    seed_products()
    seed_transfer_routes(stores)
    seed_inventory(scenario, stores)
    seed_sales(scenario)
    seed_forecasts(scenario)
    
    print(f"\n{'='*60}")
    print(f"✅ SCENARIO {scenario_num} READY!")
    print(f"   {len(stores)} stores with inventory, sales, and forecasts")
    print(f"   Run 'Agent Analysis' in the dashboard")
    print(f"{'='*60}\n")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo Data Seeder for SK Brands Retail AI")
    parser.add_argument("--scenario", type=int, choices=[1, 2], help="Scenario to seed (1 or 2)")
    parser.add_argument("--clear", action="store_true", help="Clear all demo data")
    
    args = parser.parse_args()
    
    if args.clear:
        clear_all_data()
        print("\n✅ All demo data cleared!\n")
    elif args.scenario:
        seed_scenario(args.scenario)
    else:
        print(__doc__)
        print("\nAvailable scenarios:")
        print("  1 - Winter Stock Crisis: Critical shortages across stores")
        print("  2 - Spring Sales Opportunity: Seasonal transitions")
        print("\nExamples:")
        print("  python demo_seeder.py --scenario 1")
        print("  python demo_seeder.py --scenario 2")
        print("  python demo_seeder.py --clear")

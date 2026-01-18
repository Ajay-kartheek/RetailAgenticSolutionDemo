"""
Main seeding script for the Retail Agentic AI platform.

This script creates all DynamoDB tables and populates them with mock data.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from data.schemas.tables import create_all_tables, delete_all_tables, list_tables
from data.mock.stores import generate_stores
from data.mock.products import generate_products
from data.mock.inventory import generate_inventory, get_inventory_summary
from data.mock.sales import generate_sales, get_sales_summary
from data.mock.forecasts import generate_forecasts, get_forecast_summary
from data.mock.transfers import (
    generate_store_transfers,
    generate_manufacturer_lead_times,
    get_transfer_summary,
)
from shared.db import DynamoDBClient


def seed_stores(db: DynamoDBClient) -> int:
    """Seed stores table."""
    print("\n📍 Seeding stores...")
    stores = generate_stores()
    success = db.batch_write(settings.stores_table, stores)
    if success:
        print(f"   ✓ Inserted {len(stores)} stores")
    else:
        print("   ✗ Failed to insert stores")
    return len(stores) if success else 0


def seed_products(db: DynamoDBClient) -> int:
    """Seed products table."""
    print("\n🏷️  Seeding products...")
    products = generate_products()
    success = db.batch_write(settings.products_table, products)
    if success:
        print(f"   ✓ Inserted {len(products)} products")
    else:
        print("   ✗ Failed to insert products")
    return len(products) if success else 0


def seed_inventory(db: DynamoDBClient) -> int:
    """Seed inventory table."""
    print("\n📦 Seeding inventory...")
    inventory = generate_inventory()
    summary = get_inventory_summary(inventory)

    # Batch write in chunks (DynamoDB limit is 25 items per batch)
    chunk_size = 25
    total_success = 0

    for i in range(0, len(inventory), chunk_size):
        chunk = inventory[i : i + chunk_size]
        success = db.batch_write(settings.inventory_table, chunk)
        if success:
            total_success += len(chunk)

    print(f"   ✓ Inserted {total_success} inventory items")
    print(f"   📊 Summary: {summary['low_stock_count']} low stock, {summary['out_of_stock_count']} out of stock")
    return total_success


def seed_sales(db: DynamoDBClient, days: int = 60) -> int:
    """Seed sales table with historical data."""
    print(f"\n💰 Seeding sales (last {days} days)...")
    sales = generate_sales(days_of_history=days)
    summary = get_sales_summary(sales)

    # Batch write in chunks
    chunk_size = 25
    total_success = 0

    for i in range(0, len(sales), chunk_size):
        chunk = sales[i : i + chunk_size]
        success = db.batch_write(settings.sales_table, chunk)
        if success:
            total_success += len(chunk)

        # Progress indicator
        if (i // chunk_size) % 100 == 0 and i > 0:
            print(f"   ... {total_success} records inserted")

    print(f"   ✓ Inserted {total_success} sales records")
    print(f"   📊 Total revenue: ₹{summary['total_revenue']:,.2f}")
    return total_success


def seed_forecasts(db: DynamoDBClient) -> int:
    """Seed demand forecast table."""
    print("\n📈 Seeding demand forecasts...")
    forecasts = generate_forecasts(forecast_period="2026-Q1")
    summary = get_forecast_summary(forecasts)

    success = db.batch_write(settings.demand_forecast_table, forecasts)
    if success:
        print(f"   ✓ Inserted {len(forecasts)} forecast records")
        print(f"   📊 Avg confidence: {summary['avg_confidence']}")
    else:
        print("   ✗ Failed to insert forecasts")
    return len(forecasts) if success else 0


def seed_transfers(db: DynamoDBClient) -> int:
    """Seed store transfers table."""
    print("\n🚚 Seeding store transfer routes...")
    transfers = generate_store_transfers()
    summary = get_transfer_summary(transfers)

    success = db.batch_write(settings.store_transfers_table, transfers)
    if success:
        print(f"   ✓ Inserted {len(transfers)} transfer routes")
        print(f"   📊 Avg distance: {summary['avg_distance_km']} km")
    else:
        print("   ✗ Failed to insert transfers")
    return len(transfers) if success else 0


def seed_manufacturer_lead_times(db: DynamoDBClient) -> int:
    """Seed manufacturer lead times table."""
    print("\n🏭 Seeding manufacturer lead times...")
    lead_times = generate_manufacturer_lead_times()

    success = db.batch_write(settings.manufacturer_lead_times_table, lead_times)
    if success:
        print(f"   ✓ Inserted {len(lead_times)} manufacturer records")
    else:
        print("   ✗ Failed to insert manufacturer data")
    return len(lead_times) if success else 0


def run_seeding(skip_tables: bool = False, sales_days: int = 60) -> dict:
    """
    Run the complete seeding process.

    Args:
        skip_tables: If True, skip table creation (use existing tables)
        sales_days: Number of days of sales history to generate

    Returns:
        Summary of seeding results
    """
    print("=" * 60)
    print("🚀 SK Brands - Retail Agentic AI Platform")
    print("   Database Seeding Script")
    print("=" * 60)
    print(f"\n⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "started_at": datetime.utcnow().isoformat(),
        "tables_created": False,
        "records_inserted": {},
    }

    # Step 1: Create tables
    if not skip_tables:
        print("\n📋 Creating DynamoDB tables...")
        table_results = create_all_tables()
        results["tables_created"] = all(table_results.values())
        for table, success in table_results.items():
            status = "✓" if success else "✗"
            print(f"   {status} {table}")
    else:
        print("\n📋 Skipping table creation (using existing tables)")
        existing = list_tables()
        print(f"   Found {len(existing)} existing tables")

    # Step 2: Initialize DB client
    db = DynamoDBClient()

    # Step 3: Seed data
    results["records_inserted"]["stores"] = seed_stores(db)
    results["records_inserted"]["products"] = seed_products(db)
    results["records_inserted"]["inventory"] = seed_inventory(db)
    results["records_inserted"]["sales"] = seed_sales(db, days=sales_days)
    results["records_inserted"]["forecasts"] = seed_forecasts(db)
    results["records_inserted"]["transfers"] = seed_transfers(db)
    results["records_inserted"]["manufacturer_lead_times"] = seed_manufacturer_lead_times(db)

    # Summary
    total_records = sum(results["records_inserted"].values())
    results["total_records"] = total_records
    results["completed_at"] = datetime.utcnow().isoformat()

    print("\n" + "=" * 60)
    print("✅ SEEDING COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    for table, count in results["records_inserted"].items():
        print(f"   • {table}: {count:,} records")
    print(f"\n   Total: {total_records:,} records")
    print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return results


def clear_all_data() -> None:
    """Delete all tables and data."""
    print("🗑️  Clearing all data...")
    confirm = input("Are you sure you want to delete all tables? (yes/no): ")
    if confirm.lower() == "yes":
        delete_all_tables()
        print("✓ All tables deleted")
    else:
        print("Cancelled")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed the SK Brands database")
    parser.add_argument(
        "--skip-tables",
        action="store_true",
        help="Skip table creation (use existing tables)",
    )
    parser.add_argument(
        "--sales-days",
        type=int,
        default=60,
        help="Number of days of sales history to generate (default: 60)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all tables and data",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output results to JSON file",
    )

    args = parser.parse_args()

    if args.clear:
        clear_all_data()
    else:
        results = run_seeding(
            skip_tables=args.skip_tables,
            sales_days=args.sales_days,
        )

        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"\n📄 Results saved to {args.output}")

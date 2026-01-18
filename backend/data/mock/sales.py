"""
Mock sales data generator for SK Brands stores.
"""

import random
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import Any

from .stores import STORES_DATA, STORE_CHARACTERISTICS
from .products import PRODUCTS_DATA, PRODUCT_CHARACTERISTICS


def generate_sales(days_of_history: int = 60) -> list[dict[str, Any]]:
    """
    Generate historical sales data for all stores and products.

    Creates intentional patterns for demo:
    - Trending products: Accelerating sales (velocity > expected)
    - Slow-moving products: Decelerating sales (velocity < expected)
    - Store-specific patterns based on characteristics

    Args:
        days_of_history: Number of days of historical sales to generate

    Returns:
        List of sales records ready for DynamoDB insertion.
    """
    sales_records = []
    random.seed(42)  # For reproducibility

    today = date.today()
    start_date = today - timedelta(days=days_of_history)

    for store in STORES_DATA:
        store_id = store["store_id"]
        store_chars = STORE_CHARACTERISTICS.get(store_id, {})
        demand_mult = store_chars.get("demand_multiplier", 1.0)
        trend_responsiveness = store_chars.get("trend_responsiveness", 0.5)

        for product in PRODUCTS_DATA:
            product_id = product["product_id"]
            product_chars = PRODUCT_CHARACTERISTICS.get(product_id, {})
            base_demand = product_chars.get("base_demand", 50)
            trend_factor = product_chars.get("trend_factor", 1.0)
            is_trending = product_chars.get("is_trending", False)

            base_price = float(product.get("base_price", 999))

            # Calculate daily base sales
            daily_base_sales = (base_demand * demand_mult) / 30  # Monthly demand / 30 days

            # Generate sales for each day
            for day_offset in range(days_of_history):
                sale_date = start_date + timedelta(days=day_offset)

                # Skip some days randomly (not every product sells every day)
                if random.random() < 0.15:  # 15% chance of no sale
                    continue

                # Day of week factor (weekends have higher sales)
                day_of_week = sale_date.weekday()
                if day_of_week >= 5:  # Weekend
                    dow_factor = 1.4
                else:
                    dow_factor = 1.0

                # Trend acceleration for trending products
                # More recent days have higher sales for trending items
                days_from_start = day_offset
                if is_trending:
                    # Accelerating trend - sales increase over time
                    trend_acceleration = 1.0 + (days_from_start / days_of_history) * 0.8 * trend_responsiveness
                else:
                    # Slight decay for non-trending
                    trend_acceleration = 1.0 - (days_from_start / days_of_history) * 0.1

                # Calculate daily quantity
                daily_qty = int(
                    daily_base_sales
                    * trend_factor
                    * trend_acceleration
                    * dow_factor
                    * random.uniform(0.6, 1.4)
                )

                # Ensure at least some sales
                if daily_qty < 1 and random.random() > 0.5:
                    daily_qty = 1

                if daily_qty > 0:
                    # Random discount (mostly full price, sometimes discounted)
                    if random.random() < 0.1:  # 10% chance of discount
                        discount_pct = random.choice([0.1, 0.15, 0.2])
                        discount_amount = base_price * daily_qty * discount_pct
                    else:
                        discount_amount = 0

                    revenue = (base_price * daily_qty) - discount_amount

                    store_product_id = f"{store_id}#{product_id}"

                    sales_record = {
                        "store_product_id": store_product_id,
                        "sale_date": sale_date.isoformat(),
                        "store_id": store_id,
                        "product_id": product_id,
                        "quantity_sold": daily_qty,
                        "revenue": round(revenue, 2),
                        "discount_amount": round(discount_amount, 2),
                        "channel": random.choices(["store", "online"], weights=[0.85, 0.15])[0],
                        "created_at": datetime.utcnow().isoformat(),
                    }

                    sales_records.append(sales_record)

    return sales_records


def get_sales_for_period(
    sales_records: list[dict[str, Any]],
    store_id: str,
    product_id: str,
    start_date: date,
    end_date: date,
) -> list[dict[str, Any]]:
    """Helper to filter sales for a specific period."""
    filtered = []
    for record in sales_records:
        if record["store_id"] == store_id and record["product_id"] == product_id:
            sale_date = date.fromisoformat(record["sale_date"])
            if start_date <= sale_date <= end_date:
                filtered.append(record)
    return filtered


def calculate_total_sales(
    sales_records: list[dict[str, Any]],
    store_id: str,
    product_id: str,
    start_date: date,
    end_date: date,
) -> dict[str, Any]:
    """Calculate total sales metrics for a product at a store."""
    filtered = get_sales_for_period(sales_records, store_id, product_id, start_date, end_date)

    total_qty = sum(r["quantity_sold"] for r in filtered)
    total_revenue = sum(r["revenue"] for r in filtered)
    total_discount = sum(r["discount_amount"] for r in filtered)

    return {
        "total_quantity": total_qty,
        "total_revenue": round(total_revenue, 2),
        "total_discount": round(total_discount, 2),
        "num_transactions": len(filtered),
    }


def get_sales_summary(sales_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a summary of sales for verification."""
    summary = {
        "total_records": len(sales_records),
        "total_quantity": 0,
        "total_revenue": 0,
        "by_store": {},
        "by_product": {},
    }

    for record in sales_records:
        store_id = record["store_id"]
        product_id = record["product_id"]
        qty = record["quantity_sold"]
        revenue = record["revenue"]

        summary["total_quantity"] += qty
        summary["total_revenue"] += revenue

        # By store
        if store_id not in summary["by_store"]:
            summary["by_store"][store_id] = {"quantity": 0, "revenue": 0}
        summary["by_store"][store_id]["quantity"] += qty
        summary["by_store"][store_id]["revenue"] += revenue

        # By product
        if product_id not in summary["by_product"]:
            summary["by_product"][product_id] = {"quantity": 0, "revenue": 0}
        summary["by_product"][product_id]["quantity"] += qty
        summary["by_product"][product_id]["revenue"] += revenue

    summary["total_revenue"] = round(summary["total_revenue"], 2)
    for store_id in summary["by_store"]:
        summary["by_store"][store_id]["revenue"] = round(
            summary["by_store"][store_id]["revenue"], 2
        )
    for product_id in summary["by_product"]:
        summary["by_product"][product_id]["revenue"] = round(
            summary["by_product"][product_id]["revenue"], 2
        )

    return summary

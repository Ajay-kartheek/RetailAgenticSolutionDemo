"""
Mock inventory data generator for SK Brands stores.
"""

import random
from datetime import datetime, timedelta
from typing import Any

from .stores import STORES_DATA, STORE_CHARACTERISTICS
from .products import PRODUCTS_DATA, PRODUCT_CHARACTERISTICS


def generate_inventory() -> list[dict[str, Any]]:
    """
    Generate inventory data for all stores and products.

    Creates intentional patterns for demo:
    - Chennai: Low stock on trending items (understocked scenario)
    - Tiruppur: High stock on slow-moving items (overstocked scenario)
    - Others: Mixed realistic inventory

    Returns:
        List of inventory items ready for DynamoDB insertion.
    """
    inventory_items = []
    random.seed(42)  # For reproducibility

    for store in STORES_DATA:
        store_id = store["store_id"]
        store_chars = STORE_CHARACTERISTICS.get(store_id, {})
        demand_mult = store_chars.get("demand_multiplier", 1.0)

        for product in PRODUCTS_DATA:
            product_id = product["product_id"]
            product_chars = PRODUCT_CHARACTERISTICS.get(product_id, {})
            base_demand = product_chars.get("base_demand", 50)
            is_trending = product_chars.get("is_trending", False)

            # Calculate base stock level
            base_stock = int(base_demand * demand_mult * 1.5)

            # Apply store-specific adjustments for demo scenarios
            if store_id == "STORE_CHN" and is_trending:
                # Chennai: LOW stock on trending items (creates understocked scenario)
                stock_multiplier = 0.3
            elif store_id == "STORE_TPR" and not is_trending:
                # Tiruppur: HIGH stock on slow items (creates overstocked scenario)
                stock_multiplier = 2.5
            elif store_id == "STORE_CBE" and is_trending:
                # Coimbatore: Slightly low on trending
                stock_multiplier = 0.6
            elif store_id == "STORE_VLR":
                # Vellore: Good stock on youth items (graphic tees, etc.)
                if "Graphic" in product.get("sub_category", "") or "T-Shirt" in product.get("category", ""):
                    stock_multiplier = 1.3
                else:
                    stock_multiplier = 0.8
            else:
                # Normal variation
                stock_multiplier = random.uniform(0.7, 1.3)

            final_base_stock = max(10, int(base_stock * stock_multiplier))

            # Generate inventory for each size and color combination
            sizes = product.get("sizes", ["M", "L"])
            colors = product.get("colors", ["Black"])

            for size in sizes:
                for color in colors:
                    # Distribute stock across variants with some randomness
                    # More popular sizes (M, L, 32, 34) get more stock
                    size_factor = 1.0
                    if size in ["M", "L", "32", "34"]:
                        size_factor = 1.3
                    elif size in ["S", "XL", "30", "36"]:
                        size_factor = 0.9
                    elif size in ["XS", "XXL", "28", "38", "40"]:
                        size_factor = 0.6

                    # Calculate quantity for this variant
                    variant_stock = max(
                        0,
                        int(
                            final_base_stock
                            / (len(sizes) * len(colors))
                            * size_factor
                            * random.uniform(0.8, 1.2)
                        ),
                    )

                    # Determine availability status
                    if variant_stock == 0:
                        availability = "out_of_stock"
                    elif variant_stock < 10:
                        availability = "low_stock"
                    else:
                        availability = "in_stock"

                    # Generate last restock date
                    days_ago = random.randint(1, 30)
                    restock_date = (datetime.now() - timedelta(days=days_ago)).date()

                    sku = f"{product_id}#{size}#{color}"

                    stock_status = availability  # Rename for frontend consistency
                    
                    # Calculate max stock based on reorder point + optimal batch
                    reorder_point = 15
                    max_stock = int(reorder_point * 2.5)

                    inventory_item = {
                        "store_id": store_id,
                        "sku": sku,
                        "product_id": product_id,
                        "size": size,
                        "color": color,
                        "current_stock": variant_stock,  # Renamed from quantity
                        "stock_status": stock_status,    # Renamed from availability_status
                        "reorder_point": reorder_point,  # Renamed from reorder_level
                        "max_stock": max_stock,          # Added
                        "last_restock_date": restock_date.isoformat(),
                        "location_in_store": f"Rack-{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1, 10)}",
                        "updated_at": datetime.utcnow().isoformat(),
                    }

                    inventory_items.append(inventory_item)

    return inventory_items


def get_total_inventory_by_store_product(
    inventory_items: list[dict[str, Any]], store_id: str, product_id: str
) -> int:
    """Helper to calculate total inventory for a product at a store."""
    total = 0
    for item in inventory_items:
        if item["store_id"] == store_id and item["product_id"] == product_id:
            total += item["current_stock"]
    return total


def get_inventory_summary(inventory_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a summary of inventory for verification."""
    summary = {
        "total_items": len(inventory_items),
        "by_store": {},
        "by_product": {},
        "low_stock_count": 0,
        "out_of_stock_count": 0,
    }

    for item in inventory_items:
        store_id = item["store_id"]
        product_id = item["product_id"]
        qty = item["current_stock"]  # Updated
        status = item["stock_status"] # Updated

        # By store
        if store_id not in summary["by_store"]:
            summary["by_store"][store_id] = {"total_qty": 0, "items": 0}
        summary["by_store"][store_id]["total_qty"] += qty
        summary["by_store"][store_id]["items"] += 1

        # By product
        if product_id not in summary["by_product"]:
            summary["by_product"][product_id] = {"total_qty": 0, "items": 0}
        summary["by_product"][product_id]["total_qty"] += qty
        summary["by_product"][product_id]["items"] += 1

        # Status counts
        if status == "low_stock":
            summary["low_stock_count"] += 1
        elif status == "out_of_stock":
            summary["out_of_stock_count"] += 1

    return summary

"""
Tools for the Demand Intelligence Agent.
"""

import sys
from pathlib import Path
from typing import Any
from datetime import date

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.db import DynamoDBClient
from config.settings import settings


db_client = DynamoDBClient()


def get_demand_forecasts(
    forecast_period: str = "2026-Q1",
    min_confidence: float = 0.0,
) -> dict[str, Any]:
    """
    Get all demand forecasts for a specific period.

    Args:
        forecast_period: The forecast period to retrieve (e.g., "2026-Q1")
        min_confidence: Minimum confidence score to include (0.0 to 1.0)

    Returns:
        Dictionary containing:
        - forecasts: List of forecast records
        - summary: Aggregated statistics
        - high_demand_items: Top 10 highest demand items
        - low_confidence_items: Items with confidence below 0.8
    """
    # Get forecasts for the period (limit scan for performance in demo)
    all_forecasts = db_client.scan(settings.demand_forecast_table)

    # Filter by period and confidence, limit to first 30 for demo performance
    filtered_forecasts = [
        f for f in all_forecasts
        if f.get("forecast_period") == forecast_period
        and f.get("confidence", 0) >= min_confidence
    ][:30]

    if not filtered_forecasts:
        return {
            "forecasts": [],
            "summary": {"total_forecasts": 0, "message": f"No forecasts found for period {forecast_period}"},
            "high_demand_items": [],
            "low_confidence_items": [],
        }

    # Calculate summary statistics
    total_demand = sum(f.get("forecasted_demand", 0) for f in filtered_forecasts)
    avg_confidence = sum(f.get("confidence", 0) for f in filtered_forecasts) / len(filtered_forecasts)

    # Aggregate by store
    by_store: dict[str, dict] = {}
    for f in filtered_forecasts:
        store_id = f.get("store_id", "unknown")
        if store_id not in by_store:
            by_store[store_id] = {"total_demand": 0, "count": 0, "avg_confidence": 0}
        by_store[store_id]["total_demand"] += f.get("forecasted_demand", 0)
        by_store[store_id]["count"] += 1
        by_store[store_id]["avg_confidence"] += f.get("confidence", 0)

    for store_id in by_store:
        by_store[store_id]["avg_confidence"] = round(
            by_store[store_id]["avg_confidence"] / by_store[store_id]["count"], 2
        )

    # Aggregate by product
    by_product: dict[str, dict] = {}
    for f in filtered_forecasts:
        product_id = f.get("product_id", "unknown")
        if product_id not in by_product:
            by_product[product_id] = {"total_demand": 0, "count": 0}
        by_product[product_id]["total_demand"] += f.get("forecasted_demand", 0)
        by_product[product_id]["count"] += 1

    # High demand items (top 10)
    sorted_by_demand = sorted(
        filtered_forecasts,
        key=lambda x: x.get("forecasted_demand", 0),
        reverse=True
    )
    high_demand_items = [
        {
            "store_id": f.get("store_id"),
            "product_id": f.get("product_id"),
            "forecasted_demand": f.get("forecasted_demand"),
            "confidence": f.get("confidence"),
        }
        for f in sorted_by_demand[:10]
    ]

    # Low confidence items (below 0.8)
    low_confidence_items = [
        {
            "store_id": f.get("store_id"),
            "product_id": f.get("product_id"),
            "forecasted_demand": f.get("forecasted_demand"),
            "confidence": f.get("confidence"),
        }
        for f in filtered_forecasts
        if f.get("confidence", 1.0) < 0.8
    ]

    return {
        "forecast_period": forecast_period,
        "forecasts": filtered_forecasts,
        "summary": {
            "total_forecasts": len(filtered_forecasts),
            "total_forecasted_demand": total_demand,
            "average_confidence": round(avg_confidence, 2),
            "by_store": by_store,
            "by_product": by_product,
        },
        "high_demand_items": high_demand_items,
        "low_confidence_items": low_confidence_items,
    }


def get_store_forecasts(
    store_id: str,
    forecast_period: str = "2026-Q1",
) -> dict[str, Any]:
    """
    Get demand forecasts for a specific store.

    Args:
        store_id: The store identifier (e.g., "STORE_CHN")
        forecast_period: The forecast period to retrieve

    Returns:
        Dictionary containing store-specific forecast data
    """
    # Query by store using GSI
    forecasts = db_client.scan(
        settings.demand_forecast_table,
        filter_expression=None,
    )

    # Filter for this store and period
    store_forecasts = [
        f for f in forecasts
        if f.get("store_id") == store_id
        and f.get("forecast_period") == forecast_period
    ]

    if not store_forecasts:
        return {
            "store_id": store_id,
            "forecast_period": forecast_period,
            "forecasts": [],
            "summary": {"message": f"No forecasts found for store {store_id}"},
        }

    # Sort by demand
    sorted_forecasts = sorted(
        store_forecasts,
        key=lambda x: x.get("forecasted_demand", 0),
        reverse=True
    )

    total_demand = sum(f.get("forecasted_demand", 0) for f in store_forecasts)
    avg_confidence = sum(f.get("confidence", 0) for f in store_forecasts) / len(store_forecasts)

    # Group by category (extract from product_id pattern)
    by_category: dict[str, int] = {}
    for f in store_forecasts:
        product_id = f.get("product_id", "")
        # Extract category from product_id (e.g., PROD_SHT_F01 -> Shirts)
        if "_SHT_" in product_id:
            category = "Shirts"
        elif "_TSH_" in product_id:
            category = "T-Shirts"
        elif "_TRS_" in product_id:
            category = "Trousers"
        elif "_JNS_" in product_id:
            category = "Jeans"
        elif "_ETH_" in product_id:
            category = "Ethnic"
        elif "_WIN_" in product_id:
            category = "Winter Wear"
        elif "_WMN_" in product_id:
            category = "Women"
        else:
            category = "Other"

        by_category[category] = by_category.get(category, 0) + f.get("forecasted_demand", 0)

    return {
        "store_id": store_id,
        "forecast_period": forecast_period,
        "forecasts": sorted_forecasts,
        "summary": {
            "total_products": len(store_forecasts),
            "total_forecasted_demand": total_demand,
            "average_confidence": round(avg_confidence, 2),
            "demand_by_category": by_category,
        },
        "top_5_products": [
            {
                "product_id": f.get("product_id"),
                "forecasted_demand": f.get("forecasted_demand"),
                "confidence": f.get("confidence"),
            }
            for f in sorted_forecasts[:5]
        ],
        "bottom_5_products": [
            {
                "product_id": f.get("product_id"),
                "forecasted_demand": f.get("forecasted_demand"),
                "confidence": f.get("confidence"),
            }
            for f in sorted_forecasts[-5:]
        ],
    }


def get_product_forecasts(
    product_id: str,
    forecast_period: str = "2026-Q1",
) -> dict[str, Any]:
    """
    Get demand forecasts for a specific product across all stores.

    Args:
        product_id: The product identifier (e.g., "PROD_SHT_F01")
        forecast_period: The forecast period to retrieve

    Returns:
        Dictionary containing product-specific forecast data across stores
    """
    forecasts = db_client.scan(
        settings.demand_forecast_table,
        filter_expression=None,
    )

    # Filter for this product and period
    product_forecasts = [
        f for f in forecasts
        if f.get("product_id") == product_id
        and f.get("forecast_period") == forecast_period
    ]

    if not product_forecasts:
        return {
            "product_id": product_id,
            "forecast_period": forecast_period,
            "forecasts": [],
            "summary": {"message": f"No forecasts found for product {product_id}"},
        }

    # Sort by demand (highest first)
    sorted_forecasts = sorted(
        product_forecasts,
        key=lambda x: x.get("forecasted_demand", 0),
        reverse=True
    )

    total_demand = sum(f.get("forecasted_demand", 0) for f in product_forecasts)
    avg_confidence = sum(f.get("confidence", 0) for f in product_forecasts) / len(product_forecasts)

    # Demand distribution by store
    by_store = {
        f.get("store_id"): {
            "forecasted_demand": f.get("forecasted_demand"),
            "confidence": f.get("confidence"),
        }
        for f in product_forecasts
    }

    # Identify highest and lowest demand stores
    highest_demand_store = sorted_forecasts[0].get("store_id") if sorted_forecasts else None
    lowest_demand_store = sorted_forecasts[-1].get("store_id") if sorted_forecasts else None

    return {
        "product_id": product_id,
        "forecast_period": forecast_period,
        "forecasts": sorted_forecasts,
        "summary": {
            "total_stores": len(product_forecasts),
            "total_forecasted_demand": total_demand,
            "average_demand_per_store": round(total_demand / len(product_forecasts), 1),
            "average_confidence": round(avg_confidence, 2),
            "demand_by_store": by_store,
        },
        "highest_demand_store": {
            "store_id": highest_demand_store,
            "demand": sorted_forecasts[0].get("forecasted_demand") if sorted_forecasts else 0,
        },
        "lowest_demand_store": {
            "store_id": lowest_demand_store,
            "demand": sorted_forecasts[-1].get("forecasted_demand") if sorted_forecasts else 0,
        },
    }


# Tool definitions for Strands Agents SDK
DEMAND_TOOLS = [
    {
        "name": "get_demand_forecasts",
        "description": "Get all demand forecasts for a specific period with summary statistics, high demand items, and low confidence items",
        "function": get_demand_forecasts,
        "parameters": {
            "type": "object",
            "properties": {
                "forecast_period": {
                    "type": "string",
                    "description": "The forecast period (e.g., '2026-Q1')",
                    "default": "2026-Q1",
                },
                "min_confidence": {
                    "type": "number",
                    "description": "Minimum confidence score to include (0.0 to 1.0)",
                    "default": 0.0,
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_store_forecasts",
        "description": "Get demand forecasts for a specific store with category breakdown",
        "function": get_store_forecasts,
        "parameters": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "string",
                    "description": "The store identifier (e.g., 'STORE_CHN' for Chennai)",
                },
                "forecast_period": {
                    "type": "string",
                    "description": "The forecast period (e.g., '2026-Q1')",
                    "default": "2026-Q1",
                },
            },
            "required": ["store_id"],
        },
    },
    {
        "name": "get_product_forecasts",
        "description": "Get demand forecasts for a specific product across all stores",
        "function": get_product_forecasts,
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {
                    "type": "string",
                    "description": "The product identifier (e.g., 'PROD_SHT_F01')",
                },
                "forecast_period": {
                    "type": "string",
                    "description": "The forecast period (e.g., '2026-Q1')",
                    "default": "2026-Q1",
                },
            },
            "required": ["product_id"],
        },
    },
]

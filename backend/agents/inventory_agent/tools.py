"""
Tools for the Inventory Agent.
"""

import sys
from pathlib import Path
from typing import Any
from datetime import date, datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.db import DynamoDBClient
from config.settings import settings


db_client = DynamoDBClient()


def _calculate_stock_status(stock_to_demand_ratio: float) -> str:
    """Classify stock status based on ratio."""
    if stock_to_demand_ratio < 0.5:
        return "understocked"
    elif stock_to_demand_ratio <= 1.5:
        return "in-stock"
    else:
        return "overstocked"


def _calculate_urgency(
    stock_status: str,
    trend_status: str,
    days_of_stock: float,
) -> float:
    """Calculate urgency score (0-1)."""
    urgency = 0.0

    # Stock status contribution
    if stock_status == "understocked":
        urgency += 0.4
    elif stock_status == "overstocked":
        urgency += 0.2

    # Trend contribution
    if trend_status == "in-trend" and stock_status == "understocked":
        urgency += 0.4  # Critical: trending but no stock
    elif trend_status == "no-trend" and stock_status == "overstocked":
        urgency += 0.3  # Bad: not selling and too much stock

    # Days of stock contribution
    if days_of_stock < 7:
        urgency += 0.2
    elif days_of_stock < 14:
        urgency += 0.1

    return min(urgency, 1.0)


def analyze_inventory_status(
    store_id: str,
    product_id: str,
    trend_data: dict | None = None,
    forecast_period: str = "2026-Q1",
) -> dict[str, Any]:
    """
    Analyze inventory status for a product at a store.

    Args:
        store_id: Store identifier
        product_id: Product identifier
        trend_data: Optional trend analysis data for this product
        forecast_period: Forecast period for context

    Returns:
        Inventory status analysis
    """
    # Get current inventory
    inventory_items = db_client.scan(settings.inventory_table)
    store_inventory = [
        item for item in inventory_items
        if item.get("store_id") == store_id
        and item.get("product_id") == product_id
    ]

    current_stock = sum(item.get("quantity", 0) for item in store_inventory)

    # Get forecast
    product_store_id = f"{product_id}#{store_id}"
    forecast = db_client.get_item(
        settings.demand_forecast_table,
        {"product_store_id": product_store_id, "forecast_period": forecast_period}
    )

    forecasted_demand = forecast.get("forecasted_demand", 0) if forecast else 0

    # Get sales to date
    all_sales = db_client.scan(settings.sales_table)
    period_start = date(2026, 1, 1)
    today = date.today()

    store_product_sales = [
        s for s in all_sales
        if s.get("store_id") == store_id
        and s.get("product_id") == product_id
        and period_start.isoformat() <= s.get("sale_date", "") <= today.isoformat()
    ]
    actual_sales = sum(s.get("quantity_sold", 0) for s in store_product_sales)

    # Calculate remaining demand
    remaining_demand = max(0, forecasted_demand - actual_sales)

    # Calculate stock-to-demand ratio
    if remaining_demand > 0:
        stock_to_demand_ratio = current_stock / remaining_demand
    else:
        stock_to_demand_ratio = float('inf') if current_stock > 0 else 0

    # Get trend status
    trend_status = "average"
    velocity_ratio = 1.0
    if trend_data:
        trend_status = trend_data.get("trend_status", "average")
        velocity_ratio = trend_data.get("velocity_ratio", 1.0)

    # Calculate days of stock remaining
    period_end = date(2026, 3, 31)
    days_remaining = (period_end - today).days
    if remaining_demand > 0 and days_remaining > 0:
        daily_demand = remaining_demand / days_remaining
        days_of_stock = current_stock / daily_demand if daily_demand > 0 else float('inf')
    else:
        days_of_stock = float('inf')

    # Classify stock status
    stock_status = _calculate_stock_status(stock_to_demand_ratio)

    # Calculate urgency
    urgency = _calculate_urgency(stock_status, trend_status, days_of_stock)

    # Determine if action required
    action_required = stock_status in ["understocked", "overstocked"] and urgency > 0.3

    # Generate recommended action
    if stock_status == "understocked" and trend_status == "in-trend":
        recommended_action = "URGENT: Replenish immediately - high demand, low stock"
    elif stock_status == "understocked":
        recommended_action = "Replenish stock to meet forecasted demand"
    elif stock_status == "overstocked" and trend_status in ["no-trend", "slow-moving"]:
        recommended_action = "Consider markdown or transfer to higher-demand stores"
    elif stock_status == "overstocked":
        recommended_action = "Monitor sales velocity; consider promotional support"
    else:
        recommended_action = "No action needed - inventory levels are healthy"

    # Get product name
    product = db_client.get_item(settings.products_table, {"product_id": product_id})
    product_name = product.get("product_name", product_id) if product else product_id

    return {
        "store_id": store_id,
        "product_id": product_id,
        "product_name": product_name,
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "current_stock": current_stock,
        "forecasted_demand": forecasted_demand,
        "actual_sales_to_date": actual_sales,
        "remaining_demand": remaining_demand,
        "stock_to_demand_ratio": round(stock_to_demand_ratio, 2) if stock_to_demand_ratio != float('inf') else 999,
        "days_of_stock_remaining": round(days_of_stock, 1) if days_of_stock != float('inf') else 999,
        "stock_status": stock_status,
        "trend_status": trend_status,
        "velocity_ratio": velocity_ratio,
        "urgency_score": round(urgency, 2),
        "action_required": action_required,
        "recommended_action": recommended_action,
    }





def search_inventory_items(
    min_stock_ratio: float | None = None,
    max_stock_ratio: float | None = None,
    forecast_period: str = "2026-Q1",
    limit: int = 50,
) -> dict[str, Any]:
    """
    Search for inventory items based on stock-to-demand ratio.
    
    Use this tool to find:
    - Understocked items: max_stock_ratio = 0.2 (rules say < 20%)
    - In-stock items: min_stock_ratio = 0.5, max_stock_ratio = 1.0 (approx)
    - Overstocked items: min_stock_ratio = 1.3 (rules say > 30% buffer)

    Args:
        min_stock_ratio: Minimum ratio of stock to demand (inclusive)
        max_stock_ratio: Maximum ratio of stock to demand (inclusive)
        forecast_period: Forecast period for analysis
        limit: Max items to return

    Returns:
        List of items matching criteria
    """
    # Pre-load data ONCE (Performance Optimization)
    all_inventory = db_client.scan(settings.inventory_table)
    all_forecasts = db_client.scan(settings.demand_forecast_table)
    all_products = db_client.scan(settings.products_table)
    all_sales = db_client.scan(settings.sales_table)
    
    # Create lookup dicts
    inventory_by_key = {}
    inventory_details = {}
    for inv in all_inventory:
        key = f"{inv.get('store_id')}#{inv.get('product_id')}"
        inventory_by_key[key] = inv.get("quantity", 0)
        inventory_details[key] = {
            "safety_stock": inv.get("safety_stock", 100),
            "reorder_point": inv.get("reorder_point", 80)
        }
    
    product_names = {p.get("product_id"): p.get("name", p.get("product_name", p.get("product_id"))) for p in all_products}
    
    # Calculate actual sales by store+product
    sales_by_key = {}
    period_start = "2026-01-01"
    for sale in all_sales:
        key = f"{sale.get('store_id')}#{sale.get('product_id')}"
        if sale.get("sale_date", "") >= period_start:
            sales_by_key[key] = sales_by_key.get(key, 0) + sale.get("quantity_sold", 0)
    
    # Filter forecasts for period
    period_forecasts = [f for f in all_forecasts if f.get("forecast_period") == forecast_period]

    # Calculate Trend Constraints (Dynamic Trend Calculation)
    today = date.today()
    if forecast_period == "2026-Q1":
        period_start = date(2026, 1, 1)
        period_end = date(2026, 3, 31)
    else:
        period_start = date(2026, 1, 1) # Default fallback
        period_end = date(2026, 3, 31)
        
    total_days = (period_end - period_start).days + 1
    days_elapsed = max(1, (today - period_start).days + 1)

    # REMOVED arbitrary slicing of input to ensure we check everything
    
    matched_items = []

    for forecast in period_forecasts:
        store_id = forecast.get("store_id")
        product_id = forecast.get("product_id")
        forecasted_demand = forecast.get("forecasted_demand", 0)
        
        if not store_id or not product_id:
            continue
            
        key = f"{store_id}#{product_id}"
        current_stock = inventory_by_key.get(key, 0)
        actual_sales = sales_by_key.get(key, 0)
        inv_details = inventory_details.get(key, {"safety_stock": 100, "reorder_point": 80})
        
        # Calculate remaining demand
        remaining_demand = max(0, forecasted_demand - actual_sales)
        
        # Calculate ratio
        ratio = round(current_stock / remaining_demand, 2) if remaining_demand > 0 else 999.0
        
        # Check criteria
        if min_stock_ratio is not None and ratio < min_stock_ratio:
            continue
        if max_stock_ratio is not None and ratio > max_stock_ratio:
            continue
            
        # Determine status strictly for display (logic is in the search query)
        status = "healthy"
        if ratio < 0.5: status = "understocked"
        elif ratio > 1.5: status = "overstocked"

        # Calculate Trend Status
        expected_sales = (forecasted_demand / total_days) * days_elapsed if total_days > 0 else 0
        velocity_ratio = round(actual_sales / expected_sales, 2) if expected_sales > 0 else 0
        
        trend_status = "average"
        if velocity_ratio > 1.5:
            trend_status = "in-trend"
        elif velocity_ratio >= 0.8:
            trend_status = "average"
        elif velocity_ratio >= 0.5:
            trend_status = "slow-moving"
        else:
            trend_status = "no-trend"

        item = {
            "store_id": store_id,
            "product_id": product_id,
            "product_name": product_names.get(product_id, product_id),
            "current_stock": current_stock,
            "forecasted_demand": forecasted_demand,
            "actual_sales": actual_sales,
            "remaining_demand": remaining_demand,
            "safety_stock": inv_details.get("safety_stock", 100),

            "stock_to_demand_ratio": ratio,
            "calculated_status": status,
            "trend_status": trend_status,
            "velocity_ratio": velocity_ratio
        }
        matched_items.append(item)
        
    # Sort: Ascending for low stock (urgent first), Descending for high stock (worst first)
    is_finding_low = max_stock_ratio is not None and max_stock_ratio < 1.0
    matched_items.sort(key=lambda x: x.get("stock_to_demand_ratio", 0), reverse=not is_finding_low)

    # Apply limit AFTER sorting
    if limit > 0:
        matched_items = matched_items[:limit]

    return {
        "found_count": len(matched_items),
        "criteria": {
            "min_ratio": min_stock_ratio,
            "max_ratio": max_stock_ratio
        },
        "items": matched_items
    }


INVENTORY_TOOLS = [
    {
        "name": "search_inventory_items",
        "description": "Search inventory based on stock coverage ratio to find under/overstocked items",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "min_stock_ratio": {"type": "number", "description": "Min stock/demand ratio"},
                    "max_stock_ratio": {"type": "number", "description": "Max stock/demand ratio"},
                    "forecast_period": {"type": "string", "default": "2026-Q1"},
                    "limit": {"type": "integer", "default": 50},
                },
                "required": [],
            }
        },
    },
    {
        "name": "analyze_inventory_status",
        "description": "Analyze detailed inventory status for a specific product at a specific store",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "store_id": {"type": "string", "description": "Store identifier"},
                    "product_id": {"type": "string", "description": "Product identifier"},
                    "trend_data": {"type": "object", "description": "Optional trend data"},
                    "forecast_period": {"type": "string", "default": "2026-Q1"},
                },
                "required": ["store_id", "product_id"],
            }
        },
    }
]

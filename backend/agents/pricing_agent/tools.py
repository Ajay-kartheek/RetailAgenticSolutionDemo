"""
Tools for the Pricing & Promotion Agent.
"""

import sys
from pathlib import Path
from typing import Any
from datetime import date, datetime, timedelta
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.db import DynamoDBClient
from config.settings import settings


db_client = DynamoDBClient()


def _get_pricing_recommendation(
    stock_status: str,
    trend_status: str,
    current_price: float,
) -> dict[str, Any]:
    """Determine pricing recommendation based on stock and trend."""

    if stock_status == "overstocked":
        if trend_status in ["no-trend"]:
            discount_pct = 0.18
            rec_type = "discount"
            reason = "Overstocked with no demand - aggressive discount to clear"
        elif trend_status == "slow-moving":
            discount_pct = 0.12
            rec_type = "discount"
            reason = "Overstocked and slow-moving - moderate discount"
        else:
            discount_pct = 0.05
            rec_type = "bundle"
            reason = "Overstocked but selling - light discount or bundle offer"

        new_price = current_price * (1 - discount_pct)
        change_pct = -discount_pct * 100

    elif stock_status == "understocked":
        if trend_status == "in-trend":
            increase_pct = 0.10
            rec_type = "price_increase"
            reason = "High demand, low stock - optimize margin with price increase"
        else:
            increase_pct = 0.0
            rec_type = "hold"
            reason = "Low stock but not trending - hold price and replenish"

        new_price = current_price * (1 + increase_pct)
        change_pct = increase_pct * 100

    else:  # in-stock
        if trend_status == "in-trend":
            increase_pct = 0.05
            rec_type = "price_increase"
            reason = "Trending with healthy stock - slight price increase"
            new_price = current_price * (1 + increase_pct)
            change_pct = increase_pct * 100
        elif trend_status in ["no-trend", "slow-moving"]:
            discount_pct = 0.10
            rec_type = "flash_sale"
            reason = "Adequate stock but slow sales - flash sale to stimulate"
            new_price = current_price * (1 - discount_pct)
            change_pct = -discount_pct * 100
        else:
            rec_type = "hold"
            reason = "Healthy stock and sales - maintain current pricing"
            new_price = current_price
            change_pct = 0

    return {
        "recommendation_type": rec_type,
        "recommended_price": round(new_price, 0),
        "price_change_percent": round(change_pct, 1),
        "reason": reason,
    }


def create_pricing_recommendation(
    store_id: str,
    product_id: str,
    inventory_status: dict | None = None,
    trend_status: str = "average",
) -> dict[str, Any]:
    """
    Create a pricing/promotion recommendation for a product at a store.

    Args:
        store_id: Store identifier
        product_id: Product identifier
        inventory_status: Optional inventory status data
        trend_status: Trend status from Trend Agent

    Returns:
        Pricing recommendation with expected impact
    """
    # Get product info
    product = db_client.get_item(settings.products_table, {"product_id": product_id})
    if not product:
        return {"error": f"Product {product_id} not found"}

    current_price = float(product.get("base_price", 999))
    cost_price = float(product.get("cost_price", 400))
    product_name = product.get("product_name") or product.get("name") or product_id

    # Determine stock status
    stock_status = "in-stock"
    if inventory_status:
        stock_status = inventory_status.get("stock_status", "in-stock")

    # Get pricing recommendation
    rec = _get_pricing_recommendation(stock_status, trend_status, current_price)

    # Calculate expected impact
    current_margin = current_price - cost_price
    new_margin = rec["recommended_price"] - cost_price

    # Estimate volume impact (simplified)
    if rec["price_change_percent"] < 0:
        # Discount increases volume
        volume_change = abs(rec["price_change_percent"]) * 1.5  # 1.5x elasticity
    elif rec["price_change_percent"] > 0:
        # Price increase decreases volume
        volume_change = -rec["price_change_percent"] * 0.8
    else:
        volume_change = 0

    # Estimate weekly revenue impact (assuming 100 units/week baseline)
    baseline_units = 100
    new_units = baseline_units * (1 + volume_change / 100)
    current_weekly_revenue = baseline_units * current_price
    new_weekly_revenue = new_units * rec["recommended_price"]
    revenue_impact = new_weekly_revenue - current_weekly_revenue

    # Dates
    today = date.today()
    valid_from = today + timedelta(days=1)
    valid_until = valid_from + timedelta(days=14)  # 2-week promotion

    return {
        "store_id": store_id,
        "product_id": product_id,
        "product_name": product_name,
        "current_price": current_price,
        "recommended_price": rec["recommended_price"],
        "price_change_percent": rec["price_change_percent"],
        "recommendation_type": rec["recommendation_type"],
        "stock_status": stock_status,
        "trend_status": trend_status,
        "expected_revenue_impact_weekly": round(revenue_impact, 0),
        "expected_margin_impact_weekly": round((new_margin - current_margin) * new_units, 0),
        "confidence": 0.85,
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "reasoning": rec["reason"],
        "requires_approval": abs(rec["price_change_percent"]) > 10,
        "created_at": datetime.utcnow().isoformat(),
    }


def get_all_pricing_recommendations(
    inventory_data: dict | None = None,
    trend_data: dict | None = None,
    forecast_period: str = "2026-Q1",
) -> dict[str, Any]:
    """
    Generate pricing recommendations for all products needing attention.

    Args:
        inventory_data: Inventory analysis from Inventory Agent
        trend_data: Trend analysis from Trend Agent
        forecast_period: Forecast period

    Returns:
        All pricing recommendations
    """
    recommendations = []

    # Get items from inventory data
    items_to_analyze = []

    if inventory_data:
        # Add overstocked items
        overstocked = inventory_data.get("overstocked_items", [])
        for item in overstocked:
            items_to_analyze.append({
                "store_id": item.get("store_id"),
                "product_id": item.get("product_id"),
                "stock_status": "overstocked",
                "trend_status": item.get("trend_status", "average"),
            })

        # Add understocked trending items (price increase opportunity)
        understocked = inventory_data.get("understocked_items", [])
        for item in understocked:
            if item.get("trend_status") == "in-trend":
                items_to_analyze.append({
                    "store_id": item.get("store_id"),
                    "product_id": item.get("product_id"),
                    "stock_status": "understocked",
                    "trend_status": "in-trend",
                })

    if trend_data:
        # Add slow-moving items
        slow = trend_data.get("slow_moving_products", [])
        for item in slow:
            if not any(
                i["store_id"] == item.get("store_id") and
                i["product_id"] == item.get("product_id")
                for i in items_to_analyze
            ):
                items_to_analyze.append({
                    "store_id": item.get("store_id"),
                    "product_id": item.get("product_id"),
                    "stock_status": "in-stock",
                    "trend_status": item.get("trend_status", "slow-moving"),
                })

    # Generate recommendations
    for item in items_to_analyze:
        rec = create_pricing_recommendation(
            store_id=item["store_id"],
            product_id=item["product_id"],
            inventory_status={"stock_status": item["stock_status"]},
            trend_status=item["trend_status"],
        )
        if "error" not in rec:
            recommendations.append(rec)

    # Sort by revenue impact (highest potential first)
    recommendations.sort(
        key=lambda x: abs(x.get("expected_revenue_impact_weekly", 0)),
        reverse=True
    )

    return {
        "forecast_period": forecast_period,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
        "summary": {
            "discounts": len([r for r in recommendations if r.get("price_change_percent", 0) < 0]),
            "increases": len([r for r in recommendations if r.get("price_change_percent", 0) > 0]),
            "holds": len([r for r in recommendations if r.get("price_change_percent", 0) == 0]),
            "total_expected_weekly_impact": sum(
                r.get("expected_revenue_impact_weekly", 0) for r in recommendations
            ),
        },
    }


PRICING_TOOLS = [
    {
        "name": "create_pricing_recommendation",
        "description": "Create pricing/promotion recommendation for a product",
        "function": create_pricing_recommendation,
        "parameters": {
            "type": "object",
            "properties": {
                "store_id": {"type": "string"},
                "product_id": {"type": "string"},
                "inventory_status": {"type": "object"},
                "trend_status": {"type": "string"},
            },
            "required": ["store_id", "product_id"],
        },
    },
    {
        "name": "get_all_pricing_recommendations",
        "description": "Generate pricing recommendations for all products needing attention",
        "function": get_all_pricing_recommendations,
        "parameters": {
            "type": "object",
            "properties": {
                "inventory_data": {"type": "object"},
                "trend_data": {"type": "object"},
                "forecast_period": {"type": "string"},
            },
            "required": [],
        },
    },
]

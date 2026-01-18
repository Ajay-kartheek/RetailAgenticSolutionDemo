"""
Tools for the Trend Analyser Agent.
"""

import sys
from pathlib import Path
from typing import Any
from datetime import date, datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.db import DynamoDBClient
from config.settings import settings


db_client = DynamoDBClient()


def _calculate_trend_status(velocity_ratio: float) -> str:
    """Classify trend status based on velocity ratio."""
    if velocity_ratio > 1.5:
        return "in-trend"
    elif velocity_ratio >= 0.8:
        return "average"
    elif velocity_ratio >= 0.5:
        return "slow-moving"
    else:
        return "no-trend"


def _calculate_confidence(days_elapsed: int, velocity_ratio: float) -> float:
    """
    Calculate confidence in trend classification.

    More days = more confidence. Extreme velocity ratios = more confidence.
    """
    # Base confidence from days elapsed (more data = more confident)
    days_factor = min(days_elapsed / 30, 1.0)  # Max out at 30 days

    # Velocity extremity factor (very high or very low = more confident)
    if velocity_ratio > 2.0 or velocity_ratio < 0.3:
        velocity_factor = 0.95
    elif velocity_ratio > 1.5 or velocity_ratio < 0.5:
        velocity_factor = 0.85
    else:
        velocity_factor = 0.75  # Middle ground is less certain

    # Combine factors
    confidence = (days_factor * 0.6 + velocity_factor * 0.4)
    return round(min(confidence, 0.98), 2)


def analyze_sales_trend(
    store_id: str,
    product_id: str,
    forecast_period: str = "2026-Q1",
    as_of_date: str | None = None,
    cached_sales: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Analyze the sales trend for a specific product at a specific store.

    Compares actual sales against forecasted demand to determine trend status.

    Args:
        store_id: Store identifier (e.g., "STORE_CHN")
        product_id: Product identifier (e.g., "PROD_SHT_F01")
        forecast_period: The forecast period (e.g., "2026-Q1")
        as_of_date: Analysis date (defaults to today)

    Returns:
        Trend analysis with velocity ratio and classification
    """
    # Parse as_of_date or use today
    if as_of_date:
        analysis_date = date.fromisoformat(as_of_date)
    else:
        analysis_date = date.today()

    # Define period dates based on forecast_period
    if forecast_period == "2026-Q1":
        period_start = date(2026, 1, 1)
        period_end = date(2026, 3, 31)
    else:
        # Default to Q1 2026
        period_start = date(2026, 1, 1)
        period_end = date(2026, 3, 31)

    total_days = (period_end - period_start).days + 1
    days_elapsed = (analysis_date - period_start).days + 1
    days_remaining = max(0, (period_end - analysis_date).days)

    # Get forecast data
    product_store_id = f"{product_id}#{store_id}"
    forecast = db_client.get_item(
        settings.demand_forecast_table,
        {"product_store_id": product_store_id, "forecast_period": forecast_period}
    )

    if not forecast:
        return {
            "error": f"No forecast found for {product_id} at {store_id} for {forecast_period}",
            "store_id": store_id,
            "product_id": product_id,
        }

    forecasted_demand = forecast.get("forecasted_demand", 0)

    # Get actual sales data (use cache if provided to avoid repeated scans)
    if cached_sales is not None:
        all_sales = cached_sales
    else:
        all_sales = db_client.scan(settings.sales_table)

    relevant_sales = [
        s for s in all_sales
        if s.get("store_id") == store_id
        and s.get("product_id") == product_id
        and period_start.isoformat() <= s.get("sale_date", "") <= analysis_date.isoformat()
    ]

    actual_sales = sum(s.get("quantity_sold", 0) for s in relevant_sales)

    # Calculate expected sales at this point
    expected_sales_to_date = (forecasted_demand / total_days) * days_elapsed

    # Calculate velocity ratio
    if expected_sales_to_date > 0:
        velocity_ratio = actual_sales / expected_sales_to_date
    else:
        velocity_ratio = 0.0

    # Calculate percentage of forecast sold
    if forecasted_demand > 0:
        current_velocity_percent = (actual_sales / forecasted_demand) * 100
        expected_velocity_percent = (days_elapsed / total_days) * 100
    else:
        current_velocity_percent = 0
        expected_velocity_percent = 0

    # Project total sales
    if days_elapsed > 0:
        daily_rate = actual_sales / days_elapsed
        projected_total_sales = int(daily_rate * total_days)
    else:
        projected_total_sales = 0

    # Classify trend
    trend_status = _calculate_trend_status(velocity_ratio)
    confidence = _calculate_confidence(days_elapsed, velocity_ratio)

    # Generate reasoning
    if trend_status == "in-trend":
        reasoning = (
            f"Product is selling {((velocity_ratio - 1) * 100):.0f}% faster than expected. "
            f"At current rate, will exceed forecast by {projected_total_sales - forecasted_demand} units."
        )
    elif trend_status == "average":
        reasoning = (
            f"Product is tracking close to forecast. "
            f"Velocity ratio of {velocity_ratio:.2f} indicates healthy demand."
        )
    elif trend_status == "slow-moving":
        reasoning = (
            f"Product is selling {((1 - velocity_ratio) * 100):.0f}% slower than expected. "
            f"May need promotional support or inventory redistribution."
        )
    else:  # no-trend
        reasoning = (
            f"Product is significantly underperforming with only {velocity_ratio:.0%} of expected sales. "
            f"Consider markdown or transfer to higher-demand stores."
        )

    # Get product name (would need to query products table)
    product = db_client.get_item(settings.products_table, {"product_id": product_id})
    product_name = product.get("product_name", product_id) if product else product_id

    return {
        "store_id": store_id,
        "product_id": product_id,
        "product_name": product_name,
        "analysis_date": analysis_date.isoformat(),
        "forecast_period": forecast_period,
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "forecasted_demand": forecasted_demand,
        "actual_sales_to_date": actual_sales,
        "expected_sales_to_date": round(expected_sales_to_date, 1),
        "current_velocity_percent": round(current_velocity_percent, 1),
        "expected_velocity_percent": round(expected_velocity_percent, 1),
        "velocity_ratio": round(velocity_ratio, 2),
        "trend_status": trend_status,
        "trend_confidence": confidence,
        "projected_total_sales": projected_total_sales,
        "demand_surplus_deficit": projected_total_sales - forecasted_demand,
        "reasoning": reasoning,
    }


# Cache sales data globally to avoid repeated scans
_sales_cache = None
_sales_cache_time = None

def _get_cached_sales():
    """Get cached sales data or fetch and cache it."""
    global _sales_cache, _sales_cache_time
    import time

    # Cache for 60 seconds
    if _sales_cache is None or (time.time() - (_sales_cache_time or 0)) > 60:
        _sales_cache = db_client.scan(settings.sales_table)
        _sales_cache_time = time.time()

    return _sales_cache

def get_trending_products(
    forecast_period: str = "2026-Q1",
    min_velocity_ratio: float = 1.5,
    as_of_date: str | None = None,
) -> dict[str, Any]:
    """
    Get all products that are trending (selling faster than expected).

    Args:
        forecast_period: The forecast period to analyze
        min_velocity_ratio: Minimum velocity ratio to consider as trending
        as_of_date: Analysis date (defaults to today)

    Returns:
        List of trending products with their trend analysis
    """
    # Get all forecasts
    forecasts = db_client.scan(settings.demand_forecast_table)
    period_forecasts = [f for f in forecasts if f.get("forecast_period") == forecast_period]

    # Pre-fetch sales data ONCE for all trend calculations
    cached_sales = _get_cached_sales()

    trending_products = []

    # Limit to first 5 for demo performance
    for forecast in period_forecasts[:5]:
        store_id = forecast.get("store_id")
        product_id = forecast.get("product_id")

        # Analyze trend with cached sales data
        trend = analyze_sales_trend(
            store_id=store_id,
            product_id=product_id,
            forecast_period=forecast_period,
            as_of_date=as_of_date,
            cached_sales=cached_sales,
        )

        if "error" not in trend and trend.get("velocity_ratio", 0) >= min_velocity_ratio:
            trending_products.append({
                "store_id": store_id,
                "product_id": product_id,
                "product_name": trend.get("product_name"),
                "velocity_ratio": trend.get("velocity_ratio"),
                "trend_status": trend.get("trend_status"),
                "actual_sales": trend.get("actual_sales_to_date"),
                "forecasted_demand": trend.get("forecasted_demand"),
                "current_velocity_percent": trend.get("current_velocity_percent"),
                "confidence": trend.get("trend_confidence"),
            })

    # Sort by velocity ratio (highest first)
    trending_products.sort(key=lambda x: x.get("velocity_ratio", 0), reverse=True)

    return {
        "forecast_period": forecast_period,
        "analysis_date": as_of_date or date.today().isoformat(),
        "min_velocity_ratio": min_velocity_ratio,
        "total_trending": len(trending_products),
        "trending_products": trending_products,
        "summary": {
            "by_store": _group_by_store(trending_products),
            "by_product": _group_by_product(trending_products),
        },
    }


def get_slow_moving_products(
    forecast_period: str = "2026-Q1",
    max_velocity_ratio: float = 0.8,
    as_of_date: str | None = None,
) -> dict[str, Any]:
    """
    Get all products that are slow-moving or have no trend.

    Args:
        forecast_period: The forecast period to analyze
        max_velocity_ratio: Maximum velocity ratio to consider as slow-moving
        as_of_date: Analysis date (defaults to today)

    Returns:
        List of slow-moving products with their trend analysis
    """
    # Get all forecasts
    forecasts = db_client.scan(settings.demand_forecast_table)
    period_forecasts = [f for f in forecasts if f.get("forecast_period") == forecast_period]

    # Pre-fetch sales data ONCE for all trend calculations (reuse cache)
    cached_sales = _get_cached_sales()

    slow_products = []

    # Limit to first 5 for demo performance
    for forecast in period_forecasts[:5]:
        store_id = forecast.get("store_id")
        product_id = forecast.get("product_id")

        # Analyze trend with cached sales data
        trend = analyze_sales_trend(
            store_id=store_id,
            product_id=product_id,
            forecast_period=forecast_period,
            as_of_date=as_of_date,
            cached_sales=cached_sales,
        )

        if "error" not in trend and trend.get("velocity_ratio", 1) <= max_velocity_ratio:
            slow_products.append({
                "store_id": store_id,
                "product_id": product_id,
                "product_name": trend.get("product_name"),
                "velocity_ratio": trend.get("velocity_ratio"),
                "trend_status": trend.get("trend_status"),
                "actual_sales": trend.get("actual_sales_to_date"),
                "forecasted_demand": trend.get("forecasted_demand"),
                "current_velocity_percent": trend.get("current_velocity_percent"),
                "confidence": trend.get("trend_confidence"),
                "shortfall": trend.get("forecasted_demand", 0) - trend.get("projected_total_sales", 0),
            })

    # Sort by velocity ratio (lowest first - worst performers at top)
    slow_products.sort(key=lambda x: x.get("velocity_ratio", 0))

    return {
        "forecast_period": forecast_period,
        "analysis_date": as_of_date or date.today().isoformat(),
        "max_velocity_ratio": max_velocity_ratio,
        "total_slow_moving": len(slow_products),
        "slow_moving_products": slow_products,
        "summary": {
            "by_store": _group_by_store(slow_products),
            "by_product": _group_by_product(slow_products),
        },
    }


def _group_by_store(products: list[dict]) -> dict[str, int]:
    """Group product counts by store."""
    by_store: dict[str, int] = {}
    for p in products:
        store_id = p.get("store_id", "unknown")
        by_store[store_id] = by_store.get(store_id, 0) + 1
    return by_store


def _group_by_product(products: list[dict]) -> dict[str, int]:
    """Group product counts by product ID."""
    by_product: dict[str, int] = {}
    for p in products:
        product_id = p.get("product_id", "unknown")
        by_product[product_id] = by_product.get(product_id, 0) + 1
    return by_product


# Tool definitions for Strands Agents SDK
TREND_TOOLS = [
    {
        "name": "analyze_sales_trend",
        "description": "Analyze the sales trend for a specific product at a specific store by comparing actual sales against forecasted demand",
        "function": analyze_sales_trend,
        "parameters": {
            "type": "object",
            "properties": {
                "store_id": {
                    "type": "string",
                    "description": "Store identifier (e.g., 'STORE_CHN')",
                },
                "product_id": {
                    "type": "string",
                    "description": "Product identifier (e.g., 'PROD_SHT_F01')",
                },
                "forecast_period": {
                    "type": "string",
                    "description": "Forecast period to analyze (e.g., '2026-Q1')",
                    "default": "2026-Q1",
                },
                "as_of_date": {
                    "type": "string",
                    "description": "Analysis date in ISO format (defaults to today)",
                },
            },
            "required": ["store_id", "product_id"],
        },
    },
    {
        "name": "get_trending_products",
        "description": "Get all products that are selling faster than expected (in-trend)",
        "function": get_trending_products,
        "parameters": {
            "type": "object",
            "properties": {
                "forecast_period": {
                    "type": "string",
                    "description": "Forecast period to analyze",
                    "default": "2026-Q1",
                },
                "min_velocity_ratio": {
                    "type": "number",
                    "description": "Minimum velocity ratio to consider as trending (default 1.5)",
                    "default": 1.5,
                },
                "as_of_date": {
                    "type": "string",
                    "description": "Analysis date in ISO format",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_slow_moving_products",
        "description": "Get all products that are selling slower than expected (slow-moving or no-trend)",
        "function": get_slow_moving_products,
        "parameters": {
            "type": "object",
            "properties": {
                "forecast_period": {
                    "type": "string",
                    "description": "Forecast period to analyze",
                    "default": "2026-Q1",
                },
                "max_velocity_ratio": {
                    "type": "number",
                    "description": "Maximum velocity ratio to consider as slow-moving (default 0.8)",
                    "default": 0.8,
                },
                "as_of_date": {
                    "type": "string",
                    "description": "Analysis date in ISO format",
                },
            },
            "required": [],
        },
    },
]

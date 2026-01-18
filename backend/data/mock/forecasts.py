"""
Mock demand forecast data generator (simulating ML model output).
"""

import random
from datetime import datetime, date
from typing import Any

from .stores import STORES_DATA, STORE_CHARACTERISTICS
from .products import PRODUCTS_DATA, PRODUCT_CHARACTERISTICS


def generate_forecasts(forecast_period: str = "2026-Q1") -> list[dict[str, Any]]:
    """
    Generate demand forecast data simulating SageMaker ML model output.

    Creates forecasts for Q1 2026 (Jan-Mar) for all store-product combinations.

    Args:
        forecast_period: The forecast period identifier (e.g., "2026-Q1")

    Returns:
        List of forecast records ready for DynamoDB insertion.
    """
    forecasts = []
    random.seed(42)  # For reproducibility

    # Define the forecast period
    period_start = date(2026, 1, 1)
    period_end = date(2026, 3, 31)
    period_days = (period_end - period_start).days + 1

    for store in STORES_DATA:
        store_id = store["store_id"]
        store_chars = STORE_CHARACTERISTICS.get(store_id, {})
        demand_mult = store_chars.get("demand_multiplier", 1.0)
        formal_pref = store_chars.get("formal_preference", 0.5)
        trend_resp = store_chars.get("trend_responsiveness", 0.5)

        for product in PRODUCTS_DATA:
            product_id = product["product_id"]
            product_chars = PRODUCT_CHARACTERISTICS.get(product_id, {})
            base_demand = product_chars.get("base_demand", 50)
            trend_factor = product_chars.get("trend_factor", 1.0)
            is_trending = product_chars.get("is_trending", False)

            # Determine season (Q1 = Winter transitioning to Summer)
            seasons = product.get("seasons", ["All-Season"])
            season = "Winter"  # Q1 starts with winter

            # Season adjustment
            if "Winter" in seasons or "All-Season" in seasons:
                season_factor = 1.0
            elif "Summer" in seasons:
                season_factor = 0.7  # Less demand in winter for summer items
            else:
                season_factor = 0.8

            # Category adjustment based on store preference
            category = product.get("category", "")
            sub_category = product.get("sub_category", "")

            if sub_category == "Formal" and formal_pref > 0.5:
                category_factor = 1.0 + (formal_pref - 0.5)
            elif sub_category == "Casual" and formal_pref < 0.5:
                category_factor = 1.0 + (0.5 - formal_pref)
            else:
                category_factor = 1.0

            # Trend boost for trending products at trend-responsive stores
            if is_trending:
                trend_boost = 1.0 + (trend_resp * 0.5)
            else:
                trend_boost = 1.0

            # Calculate forecasted demand for the period
            # Base: monthly demand * 3 months * adjustments
            forecasted_demand = int(
                base_demand
                * 3  # 3 months
                * demand_mult
                * season_factor
                * category_factor
                * trend_factor
                * trend_boost
                * random.uniform(0.9, 1.1)  # Small random variation
            )

            # Confidence score based on data quality factors
            # Trending items have lower confidence (more volatile)
            if is_trending:
                confidence = random.uniform(0.70, 0.85)
            else:
                confidence = random.uniform(0.80, 0.95)

            # Contributing factors for explainability
            factors = {
                "historical_sales": round(random.uniform(0.3, 0.5), 2),
                "seasonality": round(random.uniform(0.15, 0.25), 2),
                "trend_signals": round(random.uniform(0.1, 0.2), 2) if is_trending else 0.05,
                "store_performance": round(random.uniform(0.1, 0.15), 2),
                "category_growth": round(random.uniform(0.05, 0.1), 2),
            }

            product_store_id = f"{product_id}#{store_id}"

            forecast_record = {
                "product_store_id": product_store_id,
                "forecast_period": forecast_period,
                "product_id": product_id,
                "store_id": store_id,
                "season": season,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "period_days": period_days,
                "forecasted_demand": forecasted_demand,
                "confidence": round(confidence, 2),
                "forecast_model": "mock_sagemaker_v1",
                "model_version": "1.0.0",
                "factors": factors,
                "created_at": datetime.utcnow().isoformat(),
            }

            forecasts.append(forecast_record)

    return forecasts


def get_forecast_summary(forecasts: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a summary of forecasts for verification."""
    summary = {
        "total_forecasts": len(forecasts),
        "total_forecasted_demand": 0,
        "avg_confidence": 0,
        "by_store": {},
        "by_product": {},
        "high_demand_items": [],
    }

    confidences = []

    for forecast in forecasts:
        store_id = forecast["store_id"]
        product_id = forecast["product_id"]
        demand = forecast["forecasted_demand"]
        confidence = forecast["confidence"]

        summary["total_forecasted_demand"] += demand
        confidences.append(confidence)

        # By store
        if store_id not in summary["by_store"]:
            summary["by_store"][store_id] = {"total_demand": 0, "count": 0}
        summary["by_store"][store_id]["total_demand"] += demand
        summary["by_store"][store_id]["count"] += 1

        # By product
        if product_id not in summary["by_product"]:
            summary["by_product"][product_id] = {"total_demand": 0, "count": 0}
        summary["by_product"][product_id]["total_demand"] += demand
        summary["by_product"][product_id]["count"] += 1

        # Track high demand items
        if demand > 200:
            summary["high_demand_items"].append({
                "store_id": store_id,
                "product_id": product_id,
                "demand": demand,
            })

    summary["avg_confidence"] = round(sum(confidences) / len(confidences), 2) if confidences else 0
    summary["high_demand_items"] = sorted(
        summary["high_demand_items"],
        key=lambda x: x["demand"],
        reverse=True
    )[:10]  # Top 10

    return summary

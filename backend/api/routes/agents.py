"""
Agents API routes.
"""

from fastapi import APIRouter
from boto3.dynamodb.conditions import Key
import logging

from shared.db import DynamoDBClient
from config.settings import settings

router = APIRouter(prefix="/agents", tags=["agents"])
logger = logging.getLogger(__name__)

@router.get("/history")
async def get_agents_history():
    """
    Get the latest run results for all agents.
    Returns the most recent analysis for each agent type.
    """
    db = DynamoDBClient()
    table_name = settings.agent_runs_table
    
    # We want the LATEST run for each agent.
    # Since we don't have a single "latest run ID" easily accessible without querying,
    # we can query by agent_id using the GSI (agent-timestamp-index) to get the latest.
    
    agent_types = [
        "Orchestrator",
        "demand_agent", 
        "trend_agent", 
        "inventory_agent", 
        "replenishment_agent", 
        "pricing_agent", 
        "campaign_agent"
    ]
    
    history = {}
    
    try:
        for agent_id in agent_types:
            # query GSI: agent_id = :agent_id, scan_index_forward=False (descending) limit 1
            response = db.query(
                table_name=table_name,
                key_condition=Key('agent_id').eq(agent_id),
                limit=1,
                ScanIndexForward=False, # Get latest first
                index_name="agent-timestamp-index"
            )
            
            if response:
                history[agent_id] = response[0]
            else:
                # Return empty struct if no history yet
                history[agent_id] = {
                    "agent_id": agent_id,
                    "summary": "No analysis history available yet.",
                    "insights": [],
                    "recommendations": [],
                    "metrics": {}
                }
                
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Error fetching agent history: {e}")
        return {"error": str(e), "history": {}}


def _get_stored_insights(agent_type: str, period: str = "2026-Q1"):
    """
    Get stored insights for an agent type.
    Returns None if no stored insights exist (agent hasn't run yet).
    """
    db = DynamoDBClient()
    try:
        # Query the agent_insights table for this agent type
        items = db.scan(settings.agent_insights_table)
        # Filter by agent_type and period
        matching = [i for i in items if i.get("agent_type") == agent_type and i.get("forecast_period") == period]
        if matching:
            # Return the most recent one (by timestamp)
            matching.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return matching[0]
        return None
    except Exception as e:
        logger.error(f"Error fetching stored insights for {agent_type}: {e}")
        return None


def _check_agent_has_run() -> bool:
    """Check if any agent analysis has been run (agent_insights table has data)."""
    db = DynamoDBClient()
    try:
        items = db.scan(settings.agent_insights_table)
        return len(items) > 0
    except Exception:
        return False


@router.get("/status")
async def get_agents_status():
    """
    Check if agent analysis has been run.
    Returns has_data: True if agents have run and stored insights.
    """
    has_data = _check_agent_has_run()
    return {
        "has_data": has_data,
        "message": "Agent analysis data available" if has_data else "No agent analysis run yet. Please run 'Agent Analysis' first."
    }


@router.get("/demand/insights")
async def get_demand_insights(store_id: str = None, period: str = "2026-Q1"):
    """
    Get demand forecast insights for display in the Demand Agent page.
    
    Args:
        store_id: Optional store ID to filter by. If not provided, returns all stores.
        period: Forecast period (default: 2026-Q1)
    
    Returns:
        List of demand insights with product details for table display.
    """
    db = DynamoDBClient()
    
    try:
        # Get all forecasts
        forecasts = db.scan(settings.demand_forecast_table)
        
        # Filter by period
        forecasts = [f for f in forecasts if f.get("forecast_period") == period]
        
        # Filter by store if specified
        if store_id:
            forecasts = [f for f in forecasts if f.get("store_id") == store_id]
        
        # Get products for enrichment
        products = db.get_all_products()
        products_map = {p["product_id"]: p for p in products}
        
        # Get inventory data for stock info
        inventory_data = db.scan(settings.inventory_table)
        
        # Create inventory lookup by store+product
        inventory_map = {}
        for inv in inventory_data:
            key = f"{inv.get('store_id')}#{inv.get('product_id')}"
            if key not in inventory_map:
                inventory_map[key] = 0
            inventory_map[key] += inv.get("quantity", 0)
        
        # Enrich forecasts with product details and inventory
        insights = []
        for f in forecasts:
            product = products_map.get(f.get("product_id"), {})
            inv_key = f"{f.get('store_id')}#{f.get('product_id')}"
            current_stock = inventory_map.get(inv_key, 0)
            forecasted_demand = f.get("forecasted_demand", 0)
            
            # Get season from product's seasons field (array), or fallback to forecast's season
            product_seasons = product.get("seasons", [])
            if product_seasons and len(product_seasons) > 0:
                # Join multiple seasons with comma, e.g., "Winter, Monsoon"
                season = ", ".join(product_seasons)
            else:
                season = f.get("season", "All-Season")
            
            # Calculate stock status
            if current_stock == 0:
                stock_status = "out_of_stock"
            elif forecasted_demand > 0 and current_stock < forecasted_demand * 0.3:
                stock_status = "low_stock"
            elif forecasted_demand > 0 and current_stock > forecasted_demand * 1.3:
                stock_status = "overstocked"
            else:
                stock_status = "in_stock"
            
            insights.append({
                "store_id": f.get("store_id"),
                "product_id": f.get("product_id"),
                "product_name": product.get("product_name") or product.get("name") or f.get("product_id"),
                "category": product.get("category", "Unknown"),
                "forecasted_demand": forecasted_demand,
                "current_stock": current_stock,
                "confidence": f.get("confidence", 0),
                "season": season,
                "period_start": f.get("period_start"),
                "period_end": f.get("period_end"),
                "stock_status": stock_status,
                "stock_to_demand_ratio": round(current_stock / forecasted_demand, 2) if forecasted_demand > 0 else 0
            })
        
        # Sort by forecasted demand (highest first)
        insights.sort(key=lambda x: x["forecasted_demand"], reverse=True)
        
        # Calculate summary stats
        total_demand = sum(i["forecasted_demand"] for i in insights)
        avg_confidence = sum(i["confidence"] for i in insights) / len(insights) if insights else 0
        low_stock_count = sum(1 for i in insights if i["stock_status"] in ["low_stock", "out_of_stock"])
        
        return {
            "insights": insights,
            "summary": {
                "total_items": len(insights),
                "total_forecasted_demand": total_demand,
                "average_confidence": round(avg_confidence, 2),
                "low_stock_items": low_stock_count,
                "period": period
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching demand insights: {e}")
        return {"error": str(e), "insights": [], "summary": {}}


@router.get("/trend/insights")
async def get_trend_insights(store_id: str = None, period: str = "2026-Q1"):
    """
    Get trend analysis insights comparing actual sales vs forecasted demand.
    
    Args:
        store_id: Optional store ID to filter by
        period: Forecast period (default: 2026-Q1)
    
    Returns:
        List of trend insights with velocity ratios and trend status.
    """
    from datetime import date
    
    db = DynamoDBClient()
    
    try:
        # Get forecasts
        forecasts = db.scan(settings.demand_forecast_table)
        forecasts = [f for f in forecasts if f.get("forecast_period") == period]
        
        if store_id:
            forecasts = [f for f in forecasts if f.get("store_id") == store_id]
        
        # Get products for enrichment
        products = db.get_all_products()
        products_map = {p["product_id"]: p for p in products}
        
        # Get sales data
        sales_data = db.scan(settings.sales_table)
        
        # Define period dates
        if period == "2026-Q1":
            period_start = date(2026, 1, 1)
            period_end = date(2026, 3, 31)
        else:
            period_start = date(2026, 1, 1)
            period_end = date(2026, 3, 31)
        
        analysis_date = date.today()
        total_days = (period_end - period_start).days + 1
        days_elapsed = max(1, (analysis_date - period_start).days + 1)
        
        insights = []
        trending_count = 0
        slow_moving_count = 0
        
        for f in forecasts:
            store = f.get("store_id")
            product_id = f.get("product_id")
            product = products_map.get(product_id, {})
            forecasted_demand = f.get("forecasted_demand", 0)
            
            # Calculate actual sales for this store-product combo
            relevant_sales = [
                s for s in sales_data
                if s.get("store_id") == store
                and s.get("product_id") == product_id
            ]
            actual_sales = sum(s.get("quantity_sold", 0) for s in relevant_sales)
            
            # Calculate expected sales at this point in the period
            expected_sales = (forecasted_demand / total_days) * days_elapsed if total_days > 0 else 0
            
            # Calculate velocity ratio
            velocity_ratio = round(actual_sales / expected_sales, 2) if expected_sales > 0 else 0
            
            # Determine trend status
            if velocity_ratio > 1.5:
                trend_status = "in-trend"
                trending_count += 1
            elif velocity_ratio >= 0.8:
                trend_status = "average"
            elif velocity_ratio >= 0.5:
                trend_status = "slow-moving"
                slow_moving_count += 1
            else:
                trend_status = "no-trend"
                slow_moving_count += 1
            
            # Calculate projected total and surplus/deficit
            if days_elapsed > 0:
                daily_rate = actual_sales / days_elapsed
                projected_total = int(daily_rate * total_days)
            else:
                projected_total = 0
            
            surplus_deficit = projected_total - forecasted_demand
            
            # Get product seasons
            product_seasons = product.get("seasons", [])
            season = ", ".join(product_seasons) if product_seasons else "All-Season"
            
            insights.append({
                "store_id": store,
                "product_id": product_id,
                "product_name": product.get("product_name") or product.get("name") or product_id,
                "category": product.get("category", "Unknown"),
                "forecasted_demand": forecasted_demand,
                "actual_sales": actual_sales,
                "expected_sales": round(expected_sales, 1),
                "velocity_ratio": velocity_ratio,
                "trend_status": trend_status,
                "projected_total": projected_total,
                "surplus_deficit": surplus_deficit,
                "season": season,
                "days_elapsed": days_elapsed,
                "days_remaining": max(0, (period_end - analysis_date).days)
            })
        
        # Sort by velocity ratio (highest first to show trending products first)
        insights.sort(key=lambda x: x["velocity_ratio"], reverse=True)
        
        # Calculate summary stats
        total_velocity = sum(i["velocity_ratio"] for i in insights)
        avg_velocity = round(total_velocity / len(insights), 2) if insights else 0
        
        return {
            "insights": insights,
            "summary": {
                "total_items": len(insights),
                "trending_count": trending_count,
                "slow_moving_count": slow_moving_count,
                "average_velocity_ratio": avg_velocity,
                "period": period,
                "days_elapsed": days_elapsed
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching trend insights: {e}")
        return {"error": str(e), "insights": [], "summary": {}}


@router.get("/inventory/insights")
async def get_inventory_insights(store_id: str = None, period: str = "2026-Q1"):
    """
    Get inventory health insights showing stock levels vs demand.
    
    Args:
        store_id: Optional store ID to filter by
        period: Forecast period (default: 2026-Q1)
    
    Returns:
        List of inventory insights with stock health metrics.
    """
    from datetime import date
    
    db = DynamoDBClient()
    
    try:
        # Get forecasts
        forecasts = db.scan(settings.demand_forecast_table)
        forecasts = [f for f in forecasts if f.get("forecast_period") == period]
        
        if store_id:
            forecasts = [f for f in forecasts if f.get("store_id") == store_id]
        
        # Get products for enrichment
        products = db.get_all_products()
        products_map = {p["product_id"]: p for p in products}
        
        # Get inventory data
        inventory_data = db.scan(settings.inventory_table)
        
        # Create inventory lookup by store+product (aggregate all SKUs)
        inventory_map = {}
        for inv in inventory_data:
            key = f"{inv.get('store_id')}#{inv.get('product_id')}"
            if key not in inventory_map:
                inventory_map[key] = 0
            inventory_map[key] += inv.get("current_stock", 0) or inv.get("quantity", 0)
        
        # Define period dates for days of stock calculation
        if period == "2026-Q1":
            period_start = date(2026, 1, 1)
            period_end = date(2026, 3, 31)
        else:
            period_start = date(2026, 1, 1)
            period_end = date(2026, 3, 31)
        
        analysis_date = date.today()
        total_days = (period_end - period_start).days + 1
        days_elapsed = max(1, (analysis_date - period_start).days + 1)
        days_remaining = max(1, (period_end - analysis_date).days)
        
        insights = []
        understocked_count = 0
        overstocked_count = 0
        healthy_count = 0
        
        for f in forecasts:
            store = f.get("store_id")
            product_id = f.get("product_id")
            product = products_map.get(product_id, {})
            forecasted_demand = f.get("forecasted_demand", 0)
            
            # Get current stock
            inv_key = f"{store}#{product_id}"
            current_stock = inventory_map.get(inv_key, 0)
            
            # Calculate stock-to-demand ratio
            if forecasted_demand > 0:
                stock_ratio = round(current_stock / forecasted_demand, 2)
            else:
                stock_ratio = 999 if current_stock > 0 else 0
            
            # Determine stock status
            if stock_ratio < 0.5:
                stock_status = "understocked"
                understocked_count += 1
            elif stock_ratio > 1.5:
                stock_status = "overstocked"
                overstocked_count += 1
            else:
                stock_status = "healthy"
                healthy_count += 1
            
            # Calculate days of stock remaining
            if forecasted_demand > 0 and days_remaining > 0:
                remaining_demand = max(0, forecasted_demand * (days_remaining / total_days))
                if remaining_demand > 0:
                    daily_demand = remaining_demand / days_remaining
                    days_of_stock = round(current_stock / daily_demand, 1) if daily_demand > 0 else 999
                else:
                    days_of_stock = 999
            else:
                days_of_stock = 999
            
            # Get product category
            category = product.get("category", "Unknown")
            
            insights.append({
                "store_id": store,
                "product_id": product_id,
                "product_name": product.get("product_name") or product.get("name") or product_id,
                "category": category,
                "current_stock": current_stock,
                "forecasted_demand": forecasted_demand,
                "stock_ratio": stock_ratio,
                "stock_status": stock_status,
                "days_of_stock": days_of_stock if days_of_stock != 999 else None,
            })
        
        # Sort by stock ratio (lowest first - most critical items at top)
        insights.sort(key=lambda x: x["stock_ratio"])
        
        return {
            "insights": insights,
            "summary": {
                "total_items": len(insights),
                "understocked_count": understocked_count,
                "overstocked_count": overstocked_count,
                "healthy_count": healthy_count,
                "period": period,
                "days_remaining": days_remaining
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching inventory insights: {e}")
        return {"error": str(e), "insights": [], "summary": {}}


@router.get("/replenishment/insights")
async def get_replenishment_insights(store_id: str = None, period: str = "2026-Q1"):
    """
    Get replenishment plan insights for display in the Replenishment Agent page.
    
    Args:
        store_id: Optional store ID to filter by
        period: Forecast period (default: 2026-Q1)
    
    Returns:
        List of replenishment plans with details for table display.
    """
    from datetime import date
    from agents.replenishment_agent.tools import get_all_replenishment_needs
    
    db = DynamoDBClient()
    
    try:
        # Get replenishment needs using existing tool
        needs_data = get_all_replenishment_needs(
            inventory_data=None,
            forecast_period=period
        )
        
        plans = needs_data.get("plans", [])
        
        # Filter by store if specified
        if store_id:
            plans = [p for p in plans if p.get("target_store_id") == store_id]
        
        # Get products for enrichment
        products = db.get_all_products()
        products_map = {p["product_id"]: p for p in products}
        
        # Transform plans for frontend display
        insights = []
        total_cost = 0
        transfer_count = 0
        order_count = 0
        critical_count = 0
        high_count = 0
        
        for plan in plans:
            product_id = plan.get("product_id")
            product = products_map.get(product_id, {})
            
            # Determine source based on action type
            action_type = plan.get("action_type", "unknown")
            source = ""
            if action_type == "inter_store_transfer" or action_type == "combined":
                transfer_details = plan.get("transfer_details", {})
                source = transfer_details.get("from_store_id", "")
                transfer_count += 1
            elif action_type == "manufacturer_order":
                order_details = plan.get("order_details", {})
                source = order_details.get("manufacturer_name", "Manufacturer")
                order_count += 1
            
            # Count urgency
            urgency = plan.get("urgency", "normal")
            if urgency == "critical":
                critical_count += 1
            elif urgency == "high":
                high_count += 1
            
            cost = plan.get("total_cost", 0)
            total_cost += cost
            
            insights.append({
                "plan_id": plan.get("plan_id"),
                "product_id": product_id,
                "product_name": plan.get("product_name") or product.get("product_name") or product.get("name") or product_id,
                "category": product.get("category", "Unknown"),
                "target_store_id": plan.get("target_store_id"),
                "required_quantity": plan.get("required_quantity", 0),
                "action_type": action_type,
                "source": source,
                "urgency": urgency,
                "total_cost": cost,
                "expected_completion_date": plan.get("expected_completion_date"),
                "requires_approval": plan.get("requires_approval", True),
                "reasoning": plan.get("reasoning", ""),
                "risk": plan.get("risk_if_not_executed", ""),
            })
        
        # Sort by urgency (critical first)
        urgency_order = {"critical": 0, "high": 1, "normal": 2}
        insights.sort(key=lambda x: urgency_order.get(x["urgency"], 3))
        
        return {
            "insights": insights,
            "summary": {
                "total_plans": len(insights),
                "critical_count": critical_count,
                "high_count": high_count,
                "transfer_count": transfer_count,
                "order_count": order_count,
                "total_cost": round(total_cost, 2),
                "period": period
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching replenishment insights: {e}")
        return {"error": str(e), "insights": [], "summary": {}}


@router.get("/pricing/insights")
async def get_pricing_insights(store_id: str = None, period: str = "2026-Q1"):
    """
    Get pricing recommendation insights for display in the Pricing Agent page.
    
    Args:
        store_id: Optional store ID to filter by
        period: Forecast period (default: 2026-Q1)
    
    Returns:
        List of pricing recommendations with details for table display.
    """
    from agents.pricing_agent.tools import get_all_pricing_recommendations
    
    db = DynamoDBClient()
    
    try:
        # Get products for enrichment
        products = db.get_all_products()
        products_map = {p["product_id"]: p for p in products}
        
        # Build inventory and trend data from database
        # Get demand forecasts to determine trend
        forecasts = db.scan(settings.demand_forecast_table)
        period_forecasts = [f for f in forecasts if f.get("forecast_period") == period]
        
        # Get sales data for trend analysis
        sales = db.scan(settings.sales_table)
        
        # Build trend data
        trend_data = {
            "slow_moving_products": [],
            "trending_products": []
        }
        
        # Analyze trends for each product-store combination
        for forecast in period_forecasts[:20]:  # Limit for performance
            store = forecast.get("store_id")
            product_id = forecast.get("product_id")
            forecasted = forecast.get("forecasted_demand", 0)
            
            # Get actual sales
            product_sales = [s for s in sales if s.get("product_id") == product_id and s.get("store_id") == store]
            actual = sum(s.get("quantity_sold", 0) for s in product_sales)
            
            # Calculate velocity ratio
            if forecasted > 0:
                velocity = actual / (forecasted * 0.3)  # Assume ~30% of period elapsed
            else:
                velocity = 0
            
            trend_status = "average"
            if velocity < 0.7:
                trend_status = "slow-moving"
                trend_data["slow_moving_products"].append({
                    "store_id": store,
                    "product_id": product_id,
                    "trend_status": trend_status
                })
            elif velocity > 1.3:
                trend_status = "in-trend"
                trend_data["trending_products"].append({
                    "store_id": store,
                    "product_id": product_id,
                    "trend_status": trend_status
                })
        
        # Get inventory data for stock status
        inventory = db.scan(settings.inventory_table)
        inventory_data = {
            "overstocked_items": [],
            "understocked_items": []
        }
        
        # Get pricing recommendations
        pricing_data = get_all_pricing_recommendations(
            inventory_data=inventory_data,
            trend_data=trend_data,
            forecast_period=period
        )
        
        recommendations = pricing_data.get("recommendations", [])
        
        # Filter by store if specified
        if store_id:
            recommendations = [r for r in recommendations if r.get("store_id") == store_id]
        
        # Transform for frontend display
        insights = []
        discount_count = 0
        increase_count = 0
        hold_count = 0
        total_weekly_impact = 0
        
        for rec in recommendations:
            product_id = rec.get("product_id")
            product = products_map.get(product_id, {})
            
            # Count by type
            rec_type = rec.get("recommendation_type", "hold")
            change_pct = rec.get("price_change_percent", 0)
            
            if change_pct < 0:
                discount_count += 1
            elif change_pct > 0:
                increase_count += 1
            else:
                hold_count += 1
            
            weekly_impact = rec.get("expected_revenue_impact_weekly", 0)
            total_weekly_impact += weekly_impact
            
            insights.append({
                "product_id": product_id,
                "product_name": rec.get("product_name") or product.get("product_name") or product.get("name") or product_id,
                "category": product.get("category", "Unknown"),
                "store_id": rec.get("store_id"),
                "current_price": rec.get("current_price", 0),
                "recommended_price": rec.get("recommended_price", 0),
                "price_change_percent": change_pct,
                "recommendation_type": rec_type,
                "stock_status": rec.get("stock_status", "in-stock"),
                "trend_status": rec.get("trend_status", "average"),
                "expected_revenue_impact_weekly": weekly_impact,
                "confidence": rec.get("confidence", 0.85),
                "reasoning": rec.get("reasoning", ""),
                "valid_from": rec.get("valid_from"),
                "valid_until": rec.get("valid_until"),
            })
        
        # Sort by revenue impact (highest absolute impact first)
        insights.sort(key=lambda x: abs(x["expected_revenue_impact_weekly"]), reverse=True)
        
        return {
            "insights": insights,
            "summary": {
                "total_recommendations": len(insights),
                "discount_count": discount_count,
                "increase_count": increase_count,
                "hold_count": hold_count,
                "total_weekly_impact": round(total_weekly_impact, 2),
                "period": period
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching pricing insights: {e}")
        return {"error": str(e), "insights": [], "summary": {}}

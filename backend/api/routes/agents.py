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
                "product_name": product.get("product_name", f.get("product_id")),
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


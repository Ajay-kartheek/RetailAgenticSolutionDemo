"""
Store Routes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Optional
from fastapi import APIRouter, HTTPException

from shared.db import DynamoDBClient

router = APIRouter()
db = DynamoDBClient()


@router.get("")
async def list_stores():
    """Get all stores."""
    stores = db.get_all_stores()
    return {"stores": stores, "count": len(stores)}


@router.get("/{store_id}")
async def get_store(store_id: str):
    """Get a specific store by ID."""
    store = db.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")
    return store


@router.get("/{store_id}/inventory")
async def get_store_inventory(store_id: str, category: Optional[str] = None):
    """Get inventory for a specific store."""
    store = db.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")

    inventory = db.get_store_inventory(store_id)

    if category:
        inventory = [item for item in inventory if item.get("category") == category]

    return {
        "store_id": store_id,
        "inventory": inventory,
        "count": len(inventory)
    }


@router.get("/{store_id}/sales")
async def get_store_sales(store_id: str, days: int = 30):
    """Get recent sales for a specific store."""
    store = db.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")

    sales = db.get_store_sales(store_id, days=days)

    total_revenue = sum(s.get("total_amount", 0) for s in sales)
    total_units = sum(s.get("quantity", 0) for s in sales)

    return {
        "store_id": store_id,
        "days": days,
        "sales": sales,
        "count": len(sales),
        "total_revenue": total_revenue,
        "total_units": total_units
    }


@router.get("/{store_id}/forecasts")
async def get_store_forecasts(store_id: str, period: Optional[str] = None):
    """Get demand forecasts for a specific store."""
    store = db.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail=f"Store {store_id} not found")

    forecasts = db.get_store_forecasts(store_id, period=period)

    return {
        "store_id": store_id,
        "period": period,
        "forecasts": forecasts,
        "count": len(forecasts)
    }

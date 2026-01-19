"""
Inventory Routes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from typing import Optional
from fastapi import APIRouter, HTTPException

from shared.db import DynamoDBClient
from shared.models import StockStatus

router = APIRouter()
db = DynamoDBClient()


@router.get("")
async def list_inventory(
    store_id: Optional[str] = None,
    product_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Get inventory items with optional filters."""
    if store_id:
        inventory = db.get_store_inventory(store_id)
    elif product_id:
        inventory = db.get_product_inventory(product_id)
    else:
        # Get all inventory - query all stores
        stores = db.get_all_stores()
        inventory = []
        for store in stores:
            store_inventory = db.get_store_inventory(store["store_id"])
            inventory.extend(store_inventory)

    # Filter by status if provided
    if status:
        try:
            StockStatus(status)  # Validate status
            inventory = [item for item in inventory if item.get("stock_status") == status]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Valid values: {[s.value for s in StockStatus]}"
            )

    return {"inventory": inventory, "count": len(inventory)}


@router.get("/status-summary")
async def get_inventory_status_summary():
    """Get summary of inventory status across all stores."""
    stores = db.get_all_stores()

    summary = {
        "out_of_stock": 0,
        "low_stock": 0,
        "in_stock": 0,
        "by_store": {}
    }

    for store in stores:
        store_id = store["store_id"]
        inventory = db.get_store_inventory(store_id)

        store_summary = {"out_of_stock": 0, "low_stock": 0, "in_stock": 0}

        for item in inventory:
            status = item.get("stock_status", "in_stock")
            if status in store_summary:
                store_summary[status] += 1
                summary[status] += 1

        summary["by_store"][store_id] = store_summary

    return summary


@router.get("/alerts")
async def get_inventory_alerts():
    """Get inventory items that need attention (understocked or overstocked)."""
    stores = db.get_all_stores()

    alerts = {
        "understocked": [],
        "overstocked": []
    }

    for store in stores:
        inventory = db.get_store_inventory(store["store_id"])

        for item in inventory:
            status = item.get("stock_status")
            if status == "understocked":
                alerts["understocked"].append(item)
            elif status == "overstocked":
                alerts["overstocked"].append(item)

    return {
        "alerts": alerts,
        "understocked_count": len(alerts["understocked"]),
        "overstocked_count": len(alerts["overstocked"])
    }


@router.get("/transfer-routes")
async def get_transfer_routes(from_store: Optional[str] = None):
    """Get available inter-store transfer routes."""
    routes = db.get_transfer_routes(from_store_id=from_store)
    return {"routes": routes, "count": len(routes)}


@router.get("/manufacturer-lead-times")
async def get_manufacturer_lead_times():
    """Get manufacturer lead times for all products."""
    lead_times = db.get_manufacturer_lead_times()
    return {"lead_times": lead_times, "count": len(lead_times)}

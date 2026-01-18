"""
Product Routes
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
async def list_products(category: Optional[str] = None):
    """Get all products, optionally filtered by category."""
    products = db.get_all_products()

    if category:
        products = [p for p in products if p.get("category") == category]

    return {"products": products, "count": len(products)}


@router.get("/categories")
async def list_categories():
    """Get all product categories."""
    products = db.get_all_products()
    categories = list(set(p.get("category") for p in products if p.get("category")))
    categories.sort()
    return {"categories": categories}


@router.get("/{product_id}")
async def get_product(product_id: str):
    """Get a specific product by ID."""
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


@router.get("/{product_id}/inventory")
async def get_product_inventory(product_id: str):
    """Get inventory across all stores for a product."""
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    inventory = db.get_product_inventory(product_id)

    total_stock = sum(item.get("current_stock", 0) for item in inventory)
    stores_with_stock = len([item for item in inventory if item.get("current_stock", 0) > 0])

    return {
        "product_id": product_id,
        "inventory": inventory,
        "total_stock": total_stock,
        "stores_with_stock": stores_with_stock,
        "total_stores": len(inventory)
    }


@router.get("/{product_id}/forecasts")
async def get_product_forecasts(product_id: str, period: Optional[str] = None):
    """Get demand forecasts across all stores for a product."""
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

    forecasts = db.get_product_forecasts(product_id, period=period)

    total_forecast = sum(f.get("predicted_demand", 0) for f in forecasts)

    return {
        "product_id": product_id,
        "period": period,
        "forecasts": forecasts,
        "total_predicted_demand": total_forecast,
        "store_count": len(forecasts)
    }

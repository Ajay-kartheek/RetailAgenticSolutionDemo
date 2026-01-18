"""
Tools for the Store Replenishment Agent.
"""

import sys
from pathlib import Path
from typing import Any
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.db import DynamoDBClient
from config.settings import settings


db_client = DynamoDBClient()


def find_donor_stores(
    product_id: str,
    target_store_id: str,
    required_quantity: int,
) -> list[dict[str, Any]]:
    """
    Find stores that can donate stock for a product.

    Args:
        product_id: Product needing replenishment
        target_store_id: Store needing stock
        required_quantity: Quantity needed

    Returns:
        List of potential donor stores with available quantity
    """
    # Get all inventory for this product
    inventory = db_client.scan(settings.inventory_table)
    product_inventory = [
        i for i in inventory
        if i.get("product_id") == product_id
        and i.get("store_id") != target_store_id
    ]

    # Aggregate by store
    store_stock: dict[str, int] = {}
    for item in product_inventory:
        store_id = item.get("store_id")
        store_stock[store_id] = store_stock.get(store_id, 0) + item.get("quantity", 0)

    # Get transfer routes
    transfers = db_client.scan(settings.store_transfers_table)

    donors = []
    for store_id, stock in store_stock.items():
        if stock < 20:  # Don't take from stores with low stock
            continue

        # Find transfer route
        route = next(
            (t for t in transfers
             if t.get("from_store_id") == store_id
             and t.get("to_store_id") == target_store_id),
            None
        )

        if route:
            available_to_transfer = max(0, stock - 20)  # Keep minimum 20 units
            donors.append({
                "store_id": store_id,
                "current_stock": stock,
                "available_to_transfer": available_to_transfer,
                "distance_km": route.get("distance_km"),
                "travel_time_hours": route.get("travel_time_hours"),
                "cost_per_unit": route.get("transfer_cost_per_unit"),
            })

    # Sort by distance (prefer closer stores), handle None values
    donors.sort(key=lambda x: x.get("distance_km") if x.get("distance_km") is not None else 999)

    return donors


def get_manufacturer_info(product_id: str) -> dict[str, Any] | None:
    """Get manufacturer lead time info for a product."""
    lead_times = db_client.scan(settings.manufacturer_lead_times_table)
    for lt in lead_times:
        if lt.get("product_id") == product_id:
            return lt
    return None


def create_replenishment_plan(
    target_store_id: str,
    product_id: str,
    required_quantity: int,
    urgency: str = "normal",
) -> dict[str, Any]:
    """
    Create a replenishment plan for an understocked item.

    Args:
        target_store_id: Store needing stock
        product_id: Product to replenish
        required_quantity: Quantity needed
        urgency: "critical", "high", "normal"

    Returns:
        Replenishment plan with transfer/order details
    """
    plan_id = f"PLAN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6].upper()}"

    # Get product info
    product = db_client.get_item(settings.products_table, {"product_id": product_id})
    product_name = product.get("name", product_id) if product else product_id
    product_cost = float(product.get("cost", 500)) if product else 500

    # Find potential donor stores
    donors = find_donor_stores(product_id, target_store_id, required_quantity)

    # Get manufacturer info
    mfg_info = get_manufacturer_info(product_id)

    today = date.today()
    plan = {
        "plan_id": plan_id,
        "target_store_id": target_store_id,
        "product_id": product_id,
        "product_name": product_name,
        "required_quantity": required_quantity,
        "urgency": urgency,
        "action_type": None,
        "transfer_details": None,
        "order_details": None,
        "total_cost": 0,
        "expected_completion_date": None,
        "confidence": 0.9,
        "risk_if_not_executed": "",
        "reasoning": "",
        "requires_approval": True,
        "created_at": datetime.utcnow().isoformat(),
    }

    # Decision logic
    transfer_qty = 0
    order_qty = 0
    total_cost = Decimal("0")

    # Check if transfer can fulfill
    if donors:
        best_donor = donors[0]
        available = best_donor.get("available_to_transfer", 0) or 0
        cost_per_unit = best_donor.get("cost_per_unit") or 10
        distance_km = best_donor.get("distance_km") or 100
        travel_time_hours = best_donor.get("travel_time_hours") or 8

        if available >= required_quantity:
            # Full transfer from one store
            transfer_qty = required_quantity
            plan["action_type"] = "inter_store_transfer"
            transfer_cost = transfer_qty * Decimal(str(cost_per_unit))

            plan["transfer_details"] = {
                "from_store_id": best_donor["store_id"],
                "quantity": transfer_qty,
                "distance_km": distance_km,
                "travel_time_hours": travel_time_hours,
                "cost": float(transfer_cost),
            }

            completion_days = max(1, int(travel_time_hours / 8))  # Working days
            plan["expected_completion_date"] = (today + timedelta(days=completion_days)).isoformat()
            total_cost = transfer_cost

            plan["reasoning"] = (
                f"Transferring {transfer_qty} units from {best_donor['store_id']} "
                f"({best_donor['distance_km']}km away). Fastest option available."
            )

        elif available > 0 and mfg_info:
            # Partial transfer + manufacturer order
            transfer_qty = available
            order_qty = required_quantity - available
            plan["action_type"] = "combined"

            transfer_cost = transfer_qty * Decimal(str(best_donor.get("cost_per_unit", 10)))
            order_cost = order_qty * Decimal(str(mfg_info.get("cost_per_unit", product_cost)))

            plan["transfer_details"] = {
                "from_store_id": best_donor["store_id"],
                "quantity": transfer_qty,
                "distance_km": best_donor["distance_km"],
                "travel_time_hours": best_donor["travel_time_hours"],
                "cost": float(transfer_cost),
            }

            plan["order_details"] = {
                "manufacturer_id": mfg_info.get("manufacturer_id"),
                "manufacturer_name": mfg_info.get("manufacturer_name"),
                "quantity": order_qty,
                "lead_time_days": mfg_info.get("lead_time_days", 14),
                "cost": float(order_cost),
            }

            lead_time = mfg_info.get("lead_time_days", 14)
            plan["expected_completion_date"] = (today + timedelta(days=lead_time)).isoformat()
            total_cost = transfer_cost + order_cost

            plan["reasoning"] = (
                f"Hybrid approach: Transfer {transfer_qty} units from {best_donor['store_id']} "
                f"for immediate relief, order {order_qty} units from manufacturer for full replenishment."
            )

    elif mfg_info:
        # Manufacturer order only
        order_qty = required_quantity
        plan["action_type"] = "manufacturer_order"

        # Check minimum order quantity
        min_qty = mfg_info.get("minimum_order_qty", 50)
        if order_qty < min_qty:
            order_qty = min_qty

        order_cost = order_qty * Decimal(str(mfg_info.get("cost_per_unit", product_cost)))

        plan["order_details"] = {
            "manufacturer_id": mfg_info.get("manufacturer_id"),
            "manufacturer_name": mfg_info.get("manufacturer_name"),
            "quantity": order_qty,
            "lead_time_days": mfg_info.get("lead_time_days", 14),
            "cost": float(order_cost),
        }

        lead_time = mfg_info.get("lead_time_days", 14)
        plan["expected_completion_date"] = (today + timedelta(days=lead_time)).isoformat()
        total_cost = order_cost

        plan["reasoning"] = (
            f"No suitable donor stores found. Ordering {order_qty} units from "
            f"{mfg_info.get('manufacturer_name')} (lead time: {lead_time} days)."
        )

    else:
        plan["action_type"] = "manual_review"
        plan["reasoning"] = "No transfer options or manufacturer info available. Requires manual review."
        plan["confidence"] = 0.5

    plan["total_cost"] = float(total_cost)

    # Risk assessment
    if urgency == "critical":
        plan["risk_if_not_executed"] = f"HIGH RISK: Stockout imminent. Potential lost sales of {required_quantity * product_cost:.0f} INR"
    elif urgency == "high":
        plan["risk_if_not_executed"] = f"MEDIUM RISK: Stock will deplete before period end"
    else:
        plan["risk_if_not_executed"] = "LOW RISK: May impact availability but not critical"

    # Approval threshold - always require approval for demo visibility
    plan["requires_approval"] = True  # All transfers need human approval

    return plan


def get_all_replenishment_needs(
    inventory_data: dict | None = None,
    forecast_period: str = "2026-Q1",
) -> dict[str, Any]:
    """
    Get all items needing replenishment and create plans.

    Args:
        inventory_data: Optional inventory analysis from Inventory Agent
        forecast_period: Forecast period

    Returns:
        All replenishment needs with preliminary plans
    """
    from agents.inventory_agent.tools import search_inventory_items

    # Get understocked items (ratio < 0.7 for more proactive replenishment)
    understocked = search_inventory_items(
        max_stock_ratio=0.7,
        forecast_period=forecast_period,
        limit=20
    )
    items = understocked.get("items", [])

    plans = []
    for item in items:
        current_stock = item.get("current_stock", 0) or 0
        safety_stock = item.get("safety_stock", 30) or 30
        remaining_demand = item.get("remaining_demand")
        
        # Determine urgency based on stock level vs safety stock
        stock_ratio = current_stock / safety_stock if safety_stock > 0 else 0
        if current_stock == 0:
            urgency = "critical"
        elif stock_ratio < 0.3:
            urgency = "critical"
        elif stock_ratio < 0.5:
            urgency = "high"
        else:
            urgency = "normal"

        # Calculate required quantity
        # If we have forecast data, use it; otherwise use safety stock as target
        if remaining_demand is not None and remaining_demand > 0:
            required = max(0, int(remaining_demand - current_stock))
        else:
            # No forecast - aim to reach safety stock level
            required = max(0, int(safety_stock - current_stock))
        
        # Create plan if stock is below safety level or we have positive demand
        if required > 0 or current_stock < safety_stock:
            # Ensure minimum order quantity
            required = max(required, int(safety_stock - current_stock)) if current_stock < safety_stock else required
            if required > 0:
                plan = create_replenishment_plan(
                    target_store_id=item.get("store_id"),
                    product_id=item.get("product_id"),
                    required_quantity=required,
                    urgency=urgency,
                )
                plans.append(plan)

    # Sort by urgency
    urgency_order = {"critical": 0, "high": 1, "normal": 2}
    plans.sort(key=lambda x: urgency_order.get(x.get("urgency", "normal"), 3))

    return {
        "forecast_period": forecast_period,
        "total_plans": len(plans),
        "plans": plans,
        "summary": {
            "critical": len([p for p in plans if p.get("urgency") == "critical"]),
            "high": len([p for p in plans if p.get("urgency") == "high"]),
            "normal": len([p for p in plans if p.get("urgency") == "normal"]),
            "total_cost": sum(p.get("total_cost", 0) for p in plans),
            "transfers": len([p for p in plans if "transfer" in (p.get("action_type") or "")]),
            "orders": len([p for p in plans if p.get("action_type") == "manufacturer_order"]),
        },
    }


REPLENISHMENT_TOOLS = [
    {
        "name": "find_donor_stores",
        "description": "Find stores that can donate stock for inter-store transfer",
        "function": find_donor_stores,
        "parameters": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "target_store_id": {"type": "string"},
                "required_quantity": {"type": "integer"},
            },
            "required": ["product_id", "target_store_id", "required_quantity"],
        },
    },
    {
        "name": "create_replenishment_plan",
        "description": "Create a replenishment plan for an understocked item",
        "function": create_replenishment_plan,
        "parameters": {
            "type": "object",
            "properties": {
                "target_store_id": {"type": "string"},
                "product_id": {"type": "string"},
                "required_quantity": {"type": "integer"},
                "urgency": {"type": "string", "enum": ["critical", "high", "normal"]},
            },
            "required": ["target_store_id", "product_id", "required_quantity"],
        },
    },
    {
        "name": "get_all_replenishment_needs",
        "description": "Get all items needing replenishment with plans",
        "function": get_all_replenishment_needs,
        "parameters": {
            "type": "object",
            "properties": {
                "inventory_data": {"type": "object"},
                "forecast_period": {"type": "string", "default": "2026-Q1"},
            },
            "required": [],
        },
    },
]

"""
Mock data for store transfers and manufacturer lead times.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
import math

from .stores import STORES_DATA
from .products import PRODUCTS_DATA


# Store coordinates for distance calculation
STORE_COORDINATES: dict[str, tuple[float, float]] = {
    "STORE_CHN": (13.0827, 80.2707),  # Chennai
    "STORE_CBE": (11.0168, 76.9558),  # Coimbatore
    "STORE_MDU": (9.9252, 78.1198),   # Madurai
    "STORE_TCH": (10.7905, 78.7047),  # Trichy
    "STORE_SLM": (11.6643, 78.1460),  # Salem
    "STORE_TPR": (11.1085, 77.3411),  # Tiruppur
    "STORE_VLR": (12.9165, 79.1325),  # Vellore
    "STORE_TJV": (10.7870, 79.1378),  # Thanjavur
    "STORE_ERD": (11.3410, 77.7172),  # Erode
    "STORE_NGL": (8.1833, 77.4119),   # Nagercoil
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points in km."""
    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def generate_store_transfers() -> list[dict[str, Any]]:
    """
    Generate store transfer routes between all store pairs.

    Calculates realistic distances and travel times based on coordinates.

    Returns:
        List of store transfer records ready for DynamoDB insertion.
    """
    transfers = []

    store_ids = [store["store_id"] for store in STORES_DATA]

    for from_store_id in store_ids:
        for to_store_id in store_ids:
            if from_store_id == to_store_id:
                continue  # Skip self-transfers

            from_coords = STORE_COORDINATES.get(from_store_id)
            to_coords = STORE_COORDINATES.get(to_store_id)

            if not from_coords or not to_coords:
                continue

            # Calculate straight-line distance
            straight_distance = haversine_distance(
                from_coords[0], from_coords[1],
                to_coords[0], to_coords[1]
            )

            # Road distance is typically 1.3x straight-line distance
            road_distance = straight_distance * 1.3

            # Calculate travel time (assuming 50 km/h average speed for cargo)
            travel_time_hours = road_distance / 50

            # Calculate transfer cost (Rs. 2 per km per unit + fixed handling)
            cost_per_unit = Decimal(str(round(road_distance * 0.1 + 5, 2)))

            route_id = f"{from_store_id}#{to_store_id}"

            transfer_record = {
                "route_id": route_id,
                "from_store_id": from_store_id,
                "to_store_id": to_store_id,
                "distance_km": round(road_distance, 1),
                "travel_time_hours": round(travel_time_hours, 1),
                "transfer_cost_per_unit": float(cost_per_unit),
                "route_type": "road",
                "is_active": True,
                "notes": f"Road transfer from {from_store_id} to {to_store_id}",
                "created_at": datetime.utcnow().isoformat(),
            }

            transfers.append(transfer_record)

    return transfers


def generate_manufacturer_lead_times() -> list[dict[str, Any]]:
    """
    Generate manufacturer lead time data for all products.

    Creates realistic lead times based on product complexity and material.

    Returns:
        List of manufacturer lead time records ready for DynamoDB insertion.
    """
    lead_times = []

    # Define manufacturers
    manufacturers = [
        {
            "manufacturer_id": "MFG_TIRUPPUR_01",
            "manufacturer_name": "Tiruppur Textiles Pvt Ltd",
            "location": "Tiruppur, Tamil Nadu",
            "reliability_score": 0.92,
            "specialization": ["T-Shirts", "Shirts"],
        },
        {
            "manufacturer_id": "MFG_COIMBATORE_01",
            "manufacturer_name": "Kovai Garments",
            "location": "Coimbatore, Tamil Nadu",
            "reliability_score": 0.88,
            "specialization": ["Trousers", "Jeans", "Chinos"],
        },
        {
            "manufacturer_id": "MFG_CHENNAI_01",
            "manufacturer_name": "Chennai Premium Apparel",
            "location": "Chennai, Tamil Nadu",
            "reliability_score": 0.95,
            "specialization": ["Shirts", "Women Tops", "Formal"],
        },
        {
            "manufacturer_id": "MFG_KARUR_01",
            "manufacturer_name": "Karur Silk & Cotton",
            "location": "Karur, Tamil Nadu",
            "reliability_score": 0.90,
            "specialization": ["Ethnic", "Kurta", "Silk"],
        },
        {
            "manufacturer_id": "MFG_SALEM_01",
            "manufacturer_name": "Salem Woolen Mills",
            "location": "Salem, Tamil Nadu",
            "reliability_score": 0.85,
            "specialization": ["Winter Wear", "Sweater", "Jacket"],
        },
    ]

    for product in PRODUCTS_DATA:
        product_id = product["product_id"]
        category = product.get("category", "")
        sub_category = product.get("sub_category", "")
        material = product.get("material", "Cotton")

        # Find matching manufacturer based on specialization
        matched_mfg = None
        for mfg in manufacturers:
            specializations = mfg["specialization"]
            if (
                category in specializations
                or sub_category in specializations
                or any(s in material for s in specializations)
            ):
                matched_mfg = mfg
                break

        if not matched_mfg:
            # Default to Tiruppur (general apparel)
            matched_mfg = manufacturers[0]

        # Calculate lead time based on product complexity
        base_lead_time = 10  # Base: 10 days

        # Adjustments
        if "Silk" in material:
            base_lead_time += 5  # Premium material takes longer
        if "Ethnic" in category or "Kurta" in sub_category:
            base_lead_time += 3  # Traditional wear needs more craftsmanship
        if "Winter" in category:
            base_lead_time += 4  # Specialized winter items
        if "Formal" in sub_category:
            base_lead_time += 2  # Quality control for formal wear

        # Minimum order quantity based on product type
        if "T-Shirts" in category or "Round Neck" in sub_category:
            min_order = 200  # High volume items
        elif "Ethnic" in category:
            min_order = 50  # Lower volume ethnic wear
        elif "Winter" in category:
            min_order = 75  # Seasonal items
        else:
            min_order = 100  # Standard

        # Cost per unit (slightly below retail cost price)
        cost_price = float(product.get("cost_price", 400))
        mfg_cost = cost_price * 0.85  # 15% margin for brand

        lead_time_record = {
            "product_id": product_id,
            "manufacturer_id": matched_mfg["manufacturer_id"],
            "manufacturer_name": matched_mfg["manufacturer_name"],
            "location": matched_mfg["location"],
            "lead_time_days": base_lead_time,
            "minimum_order_qty": min_order,
            "cost_per_unit": round(mfg_cost, 2),
            "reliability_score": matched_mfg["reliability_score"],
            "payment_terms": "Net 30",
            "notes": f"Standard manufacturing for {product.get('product_name', product_id)}",
            "created_at": datetime.utcnow().isoformat(),
        }

        lead_times.append(lead_time_record)

    return lead_times


def get_nearest_stores_with_stock(
    target_store_id: str,
    transfers: list[dict[str, Any]],
    max_distance_km: float = 300,
) -> list[dict[str, Any]]:
    """
    Get stores nearest to target store within a maximum distance.

    Args:
        target_store_id: The store needing stock
        transfers: List of transfer routes
        max_distance_km: Maximum distance to consider

    Returns:
        List of nearby stores sorted by distance
    """
    nearby = []

    for transfer in transfers:
        if transfer["to_store_id"] == target_store_id:
            if transfer["distance_km"] <= max_distance_km:
                nearby.append({
                    "store_id": transfer["from_store_id"],
                    "distance_km": transfer["distance_km"],
                    "travel_time_hours": transfer["travel_time_hours"],
                    "cost_per_unit": transfer["transfer_cost_per_unit"],
                })

    return sorted(nearby, key=lambda x: x["distance_km"])


def get_transfer_summary(transfers: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a summary of transfer routes for verification."""
    summary = {
        "total_routes": len(transfers),
        "avg_distance_km": 0,
        "avg_travel_time_hours": 0,
        "avg_cost_per_unit": 0,
        "shortest_route": None,
        "longest_route": None,
    }

    if not transfers:
        return summary

    distances = [t["distance_km"] for t in transfers]
    times = [t["travel_time_hours"] for t in transfers]
    costs = [t["transfer_cost_per_unit"] for t in transfers]

    summary["avg_distance_km"] = round(sum(distances) / len(distances), 1)
    summary["avg_travel_time_hours"] = round(sum(times) / len(times), 1)
    summary["avg_cost_per_unit"] = round(sum(costs) / len(costs), 2)

    min_idx = distances.index(min(distances))
    max_idx = distances.index(max(distances))

    summary["shortest_route"] = {
        "route": transfers[min_idx]["route_id"],
        "distance_km": transfers[min_idx]["distance_km"],
    }
    summary["longest_route"] = {
        "route": transfers[max_idx]["route_id"],
        "distance_km": transfers[max_idx]["distance_km"],
    }

    return summary

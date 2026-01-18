"""
Mock data for SK Brands stores across Tamil Nadu.
"""

from datetime import datetime
from typing import Any

# ============================================================================
# Store Data - 10 Tamil Nadu Cities
# ============================================================================

STORES_DATA: list[dict[str, Any]] = [
    {
        "store_id": "STORE_CHN",
        "store_name": "SK Brands - Chennai",
        "city": "Chennai",
        "region": "Tamil Nadu",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "capacity": 8000,
        "store_type": "flagship",
        "manager_name": "Rajesh Kumar",
        "contact_phone": "+91 44 2345 6789",
        "address": "123 Anna Salai, T. Nagar, Chennai - 600017",
        "notes": "Metro city, highest footfall, corporate clientele",
        "created_at": datetime(2020, 1, 15).isoformat(),
    },
    {
        "store_id": "STORE_CBE",
        "store_name": "SK Brands - Coimbatore",
        "city": "Coimbatore",
        "region": "Tamil Nadu",
        "latitude": 11.0168,
        "longitude": 76.9558,
        "capacity": 6000,
        "store_type": "flagship",
        "manager_name": "Priya Venkatesh",
        "contact_phone": "+91 422 234 5678",
        "address": "45 DB Road, RS Puram, Coimbatore - 641002",
        "notes": "Industrial hub, strong corporate wear demand",
        "created_at": datetime(2020, 3, 20).isoformat(),
    },
    {
        "store_id": "STORE_MDU",
        "store_name": "SK Brands - Madurai",
        "city": "Madurai",
        "region": "Tamil Nadu",
        "latitude": 9.9252,
        "longitude": 78.1198,
        "capacity": 5000,
        "store_type": "standard",
        "manager_name": "Selvam Murugan",
        "contact_phone": "+91 452 234 5678",
        "address": "78 West Masi Street, Madurai - 625001",
        "notes": "Temple city, traditional + modern mix, festive spikes",
        "created_at": datetime(2020, 6, 10).isoformat(),
    },
    {
        "store_id": "STORE_TCH",
        "store_name": "SK Brands - Trichy",
        "city": "Tiruchirappalli",
        "region": "Tamil Nadu",
        "latitude": 10.7905,
        "longitude": 78.7047,
        "capacity": 4500,
        "store_type": "standard",
        "manager_name": "Karthik Rajan",
        "contact_phone": "+91 431 234 5678",
        "address": "23 Thillai Nagar Main Road, Trichy - 620018",
        "notes": "Central TN hub, balanced demand across categories",
        "created_at": datetime(2020, 8, 5).isoformat(),
    },
    {
        "store_id": "STORE_SLM",
        "store_name": "SK Brands - Salem",
        "city": "Salem",
        "region": "Tamil Nadu",
        "latitude": 11.6643,
        "longitude": 78.1460,
        "capacity": 4000,
        "store_type": "standard",
        "manager_name": "Gopal Krishnan",
        "contact_phone": "+91 427 234 5678",
        "address": "56 Omalur Road, Salem - 636004",
        "notes": "Steel city, industrial workers and business owners",
        "created_at": datetime(2021, 1, 12).isoformat(),
    },
    {
        "store_id": "STORE_TPR",
        "store_name": "SK Brands - Tiruppur",
        "city": "Tiruppur",
        "region": "Tamil Nadu",
        "latitude": 11.1085,
        "longitude": 77.3411,
        "capacity": 4000,
        "store_type": "standard",
        "manager_name": "Senthil Kumar",
        "contact_phone": "+91 421 234 5678",
        "address": "89 Kumaran Road, Tiruppur - 641601",
        "notes": "Knitwear capital, local competition, price sensitive",
        "created_at": datetime(2021, 4, 18).isoformat(),
    },
    {
        "store_id": "STORE_VLR",
        "store_name": "SK Brands - Vellore",
        "city": "Vellore",
        "region": "Tamil Nadu",
        "latitude": 12.9165,
        "longitude": 79.1325,
        "capacity": 3500,
        "store_type": "standard",
        "manager_name": "Anand Babu",
        "contact_phone": "+91 416 234 5678",
        "address": "34 Officers Line, Vellore - 632001",
        "notes": "Education hub (VIT, CMC), youth demographic",
        "created_at": datetime(2021, 7, 22).isoformat(),
    },
    {
        "store_id": "STORE_TJV",
        "store_name": "SK Brands - Thanjavur",
        "city": "Thanjavur",
        "region": "Tamil Nadu",
        "latitude": 10.7870,
        "longitude": 79.1378,
        "capacity": 3500,
        "store_type": "standard",
        "manager_name": "Murugesan Pillai",
        "contact_phone": "+91 4362 23 4567",
        "address": "12 South Main Street, Thanjavur - 613001",
        "notes": "Cultural center, heritage tourism, festive demand",
        "created_at": datetime(2021, 10, 8).isoformat(),
    },
    {
        "store_id": "STORE_ERD",
        "store_name": "SK Brands - Erode",
        "city": "Erode",
        "region": "Tamil Nadu",
        "latitude": 11.3410,
        "longitude": 77.7172,
        "capacity": 3500,
        "store_type": "standard",
        "manager_name": "Palani Samy",
        "contact_phone": "+91 424 234 5678",
        "address": "67 EVN Road, Erode - 638001",
        "notes": "Turmeric city, agricultural region, seasonal patterns",
        "created_at": datetime(2022, 2, 14).isoformat(),
    },
    {
        "store_id": "STORE_NGL",
        "store_name": "SK Brands - Nagercoil",
        "city": "Nagercoil",
        "region": "Tamil Nadu",
        "latitude": 8.1833,
        "longitude": 77.4119,
        "capacity": 3000,
        "store_type": "standard",
        "manager_name": "David Raj",
        "contact_phone": "+91 4652 23 4567",
        "address": "45 Court Road, Nagercoil - 629001",
        "notes": "Southern tip, different climate (more tropical), coastal influence",
        "created_at": datetime(2022, 5, 30).isoformat(),
    },
]


def generate_stores() -> list[dict[str, Any]]:
    """
    Generate store data for seeding.

    Returns:
        List of store dictionaries ready for DynamoDB insertion.
    """
    return STORES_DATA.copy()


# Store characteristics for demand/inventory simulation
STORE_CHARACTERISTICS: dict[str, dict[str, Any]] = {
    "STORE_CHN": {
        "demand_multiplier": 1.5,  # Highest demand
        "formal_preference": 0.7,  # High formal wear preference
        "price_sensitivity": 0.3,  # Low price sensitivity
        "trend_responsiveness": 0.9,  # Very trend responsive
    },
    "STORE_CBE": {
        "demand_multiplier": 1.2,
        "formal_preference": 0.6,
        "price_sensitivity": 0.4,
        "trend_responsiveness": 0.7,
    },
    "STORE_MDU": {
        "demand_multiplier": 1.0,
        "formal_preference": 0.4,  # More traditional
        "price_sensitivity": 0.6,
        "trend_responsiveness": 0.5,
    },
    "STORE_TCH": {
        "demand_multiplier": 0.9,
        "formal_preference": 0.5,
        "price_sensitivity": 0.5,
        "trend_responsiveness": 0.6,
    },
    "STORE_SLM": {
        "demand_multiplier": 0.8,
        "formal_preference": 0.5,
        "price_sensitivity": 0.6,
        "trend_responsiveness": 0.5,
    },
    "STORE_TPR": {
        "demand_multiplier": 0.7,  # Lower due to local competition
        "formal_preference": 0.3,
        "price_sensitivity": 0.8,  # Very price sensitive
        "trend_responsiveness": 0.4,
    },
    "STORE_VLR": {
        "demand_multiplier": 0.85,
        "formal_preference": 0.4,
        "price_sensitivity": 0.7,  # Student population
        "trend_responsiveness": 0.8,  # Young demographic
    },
    "STORE_TJV": {
        "demand_multiplier": 0.75,
        "formal_preference": 0.35,
        "price_sensitivity": 0.6,
        "trend_responsiveness": 0.4,
    },
    "STORE_ERD": {
        "demand_multiplier": 0.7,
        "formal_preference": 0.4,
        "price_sensitivity": 0.7,
        "trend_responsiveness": 0.5,
    },
    "STORE_NGL": {
        "demand_multiplier": 0.6,  # Smallest market
        "formal_preference": 0.3,
        "price_sensitivity": 0.7,
        "trend_responsiveness": 0.5,
    },
}


def get_store_characteristic(store_id: str, characteristic: str) -> float:
    """Get a specific characteristic value for a store."""
    return STORE_CHARACTERISTICS.get(store_id, {}).get(characteristic, 0.5)

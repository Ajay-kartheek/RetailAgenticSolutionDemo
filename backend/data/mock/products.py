"""
Mock data for SK Brands product catalog.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

# ============================================================================
# Product Catalog - Shirts, Trousers, T-Shirts, etc.
# ============================================================================

PRODUCTS_DATA: list[dict[str, Any]] = [
    # ========================================================================
    # SHIRTS - Formal
    # ========================================================================
    {
        "product_id": "PROD_SHT_F01",
        "product_name": "Premium Cotton Formal Shirt",
        "category": "Shirts",
        "sub_category": "Formal",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Office", "Meeting", "Interview"],
        "base_price": Decimal("1499"),
        "cost_price": Decimal("600"),
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["White", "Light Blue", "Pink", "Lavender"],
        "brand": "SK Brands",
        "material": "100% Cotton",
        "sku_prefix": "SKB-SHT-F01",
        "created_at": datetime(2023, 1, 1).isoformat(),
    },
    {
        "product_id": "PROD_SHT_F02",
        "product_name": "Executive Slim Fit Shirt",
        "category": "Shirts",
        "sub_category": "Formal",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Office", "Business"],
        "base_price": Decimal("1799"),
        "cost_price": Decimal("720"),
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["White", "Sky Blue", "Grey"],
        "brand": "SK Brands",
        "material": "Cotton Blend",
        "sku_prefix": "SKB-SHT-F02",
        "created_at": datetime(2023, 1, 1).isoformat(),
    },
    {
        "product_id": "PROD_SHT_F03",
        "product_name": "Classic Check Formal Shirt",
        "category": "Shirts",
        "sub_category": "Formal",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Office", "Casual Friday"],
        "base_price": Decimal("1299"),
        "cost_price": Decimal("520"),
        "sizes": ["M", "L", "XL", "XXL"],
        "colors": ["Blue Check", "Grey Check", "Black Check"],
        "brand": "SK Brands",
        "material": "Cotton",
        "sku_prefix": "SKB-SHT-F03",
        "created_at": datetime(2023, 3, 15).isoformat(),
    },
    # ========================================================================
    # SHIRTS - Casual
    # ========================================================================
    {
        "product_id": "PROD_SHT_C01",
        "product_name": "Casual Linen Shirt",
        "category": "Shirts",
        "sub_category": "Casual",
        "gender": "Male",
        "seasons": ["Summer"],
        "occasions": ["Casual", "Weekend", "Beach"],
        "base_price": Decimal("1199"),
        "cost_price": Decimal("480"),
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["White", "Beige", "Light Green", "Sky Blue"],
        "brand": "SK Brands",
        "material": "Linen",
        "sku_prefix": "SKB-SHT-C01",
        "created_at": datetime(2023, 2, 1).isoformat(),
    },
    {
        "product_id": "PROD_SHT_C02",
        "product_name": "Printed Casual Shirt",
        "category": "Shirts",
        "sub_category": "Casual",
        "gender": "Male",
        "seasons": ["Summer", "Monsoon"],
        "occasions": ["Casual", "Party", "Outing"],
        "base_price": Decimal("999"),
        "cost_price": Decimal("400"),
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Floral Blue", "Tropical Print", "Abstract"],
        "brand": "SK Brands",
        "material": "Cotton",
        "sku_prefix": "SKB-SHT-C02",
        "created_at": datetime(2023, 4, 1).isoformat(),
    },
    # ========================================================================
    # T-SHIRTS
    # ========================================================================
    {
        "product_id": "PROD_TSH_01",
        "product_name": "Classic Polo T-Shirt",
        "category": "T-Shirts",
        "sub_category": "Polo",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Casual", "Sports", "Weekend"],
        "base_price": Decimal("799"),
        "cost_price": Decimal("320"),
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Navy", "Black", "White", "Maroon", "Green"],
        "brand": "SK Brands",
        "material": "Cotton Pique",
        "sku_prefix": "SKB-TSH-01",
        "created_at": datetime(2023, 1, 15).isoformat(),
    },
    {
        "product_id": "PROD_TSH_02",
        "product_name": "Round Neck Cotton T-Shirt",
        "category": "T-Shirts",
        "sub_category": "Round Neck",
        "gender": "Male",
        "seasons": ["Summer", "All-Season"],
        "occasions": ["Casual", "Home", "Gym"],
        "base_price": Decimal("499"),
        "cost_price": Decimal("200"),
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Black", "White", "Grey", "Navy", "Red"],
        "brand": "SK Brands",
        "material": "100% Cotton",
        "sku_prefix": "SKB-TSH-02",
        "created_at": datetime(2023, 1, 15).isoformat(),
    },
    {
        "product_id": "PROD_TSH_03",
        "product_name": "Graphic Print T-Shirt",
        "category": "T-Shirts",
        "sub_category": "Graphic",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Casual", "College", "Outing"],
        "base_price": Decimal("599"),
        "cost_price": Decimal("240"),
        "sizes": ["S", "M", "L", "XL"],
        "colors": ["Black", "White", "Navy"],
        "brand": "SK Brands",
        "material": "Cotton",
        "sku_prefix": "SKB-TSH-03",
        "created_at": datetime(2023, 5, 1).isoformat(),
    },
    # ========================================================================
    # TROUSERS - Formal
    # ========================================================================
    {
        "product_id": "PROD_TRS_F01",
        "product_name": "Classic Formal Trousers",
        "category": "Trousers",
        "sub_category": "Formal",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Office", "Meeting", "Interview"],
        "base_price": Decimal("1299"),
        "cost_price": Decimal("520"),
        "sizes": ["30", "32", "34", "36", "38", "40"],
        "colors": ["Black", "Navy", "Grey", "Brown"],
        "brand": "SK Brands",
        "material": "Polyester Blend",
        "sku_prefix": "SKB-TRS-F01",
        "created_at": datetime(2023, 1, 1).isoformat(),
    },
    {
        "product_id": "PROD_TRS_F02",
        "product_name": "Slim Fit Formal Trousers",
        "category": "Trousers",
        "sub_category": "Formal",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Office", "Business"],
        "base_price": Decimal("1499"),
        "cost_price": Decimal("600"),
        "sizes": ["28", "30", "32", "34", "36"],
        "colors": ["Black", "Charcoal", "Navy"],
        "brand": "SK Brands",
        "material": "Cotton Blend",
        "sku_prefix": "SKB-TRS-F02",
        "created_at": datetime(2023, 2, 15).isoformat(),
    },
    # ========================================================================
    # TROUSERS - Casual (Chinos)
    # ========================================================================
    {
        "product_id": "PROD_TRS_C01",
        "product_name": "Cotton Chinos",
        "category": "Trousers",
        "sub_category": "Chinos",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Casual", "Smart Casual", "Weekend"],
        "base_price": Decimal("1099"),
        "cost_price": Decimal("440"),
        "sizes": ["30", "32", "34", "36", "38"],
        "colors": ["Khaki", "Navy", "Olive", "Beige"],
        "brand": "SK Brands",
        "material": "100% Cotton",
        "sku_prefix": "SKB-TRS-C01",
        "created_at": datetime(2023, 3, 1).isoformat(),
    },
    # ========================================================================
    # JEANS
    # ========================================================================
    {
        "product_id": "PROD_JNS_01",
        "product_name": "Classic Denim Jeans",
        "category": "Jeans",
        "sub_category": "Regular Fit",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Casual", "Weekend", "Outing"],
        "base_price": Decimal("1499"),
        "cost_price": Decimal("600"),
        "sizes": ["30", "32", "34", "36", "38"],
        "colors": ["Dark Blue", "Light Blue", "Black"],
        "brand": "SK Brands",
        "material": "Denim",
        "sku_prefix": "SKB-JNS-01",
        "created_at": datetime(2023, 1, 1).isoformat(),
    },
    {
        "product_id": "PROD_JNS_02",
        "product_name": "Slim Fit Stretch Jeans",
        "category": "Jeans",
        "sub_category": "Slim Fit",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Casual", "Party", "Dating"],
        "base_price": Decimal("1799"),
        "cost_price": Decimal("720"),
        "sizes": ["28", "30", "32", "34", "36"],
        "colors": ["Dark Indigo", "Black", "Grey"],
        "brand": "SK Brands",
        "material": "Stretch Denim",
        "sku_prefix": "SKB-JNS-02",
        "created_at": datetime(2023, 4, 1).isoformat(),
    },
    # ========================================================================
    # ETHNIC WEAR
    # ========================================================================
    {
        "product_id": "PROD_ETH_01",
        "product_name": "Silk Kurta",
        "category": "Ethnic",
        "sub_category": "Kurta",
        "gender": "Male",
        "seasons": ["All-Season"],
        "occasions": ["Festival", "Wedding", "Puja"],
        "base_price": Decimal("1999"),
        "cost_price": Decimal("800"),
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Gold", "Maroon", "Royal Blue", "White"],
        "brand": "SK Brands",
        "material": "Silk",
        "sku_prefix": "SKB-ETH-01",
        "created_at": datetime(2023, 1, 1).isoformat(),
    },
    {
        "product_id": "PROD_ETH_02",
        "product_name": "Cotton Kurta",
        "category": "Ethnic",
        "sub_category": "Kurta",
        "gender": "Male",
        "seasons": ["Summer", "All-Season"],
        "occasions": ["Casual", "Festival", "Temple"],
        "base_price": Decimal("999"),
        "cost_price": Decimal("400"),
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["White", "Cream", "Light Blue", "Yellow"],
        "brand": "SK Brands",
        "material": "Cotton",
        "sku_prefix": "SKB-ETH-02",
        "created_at": datetime(2023, 6, 1).isoformat(),
    },
    # ========================================================================
    # WINTER WEAR
    # ========================================================================
    {
        "product_id": "PROD_WIN_01",
        "product_name": "Wool Blend Sweater",
        "category": "Winter Wear",
        "sub_category": "Sweater",
        "gender": "Male",
        "seasons": ["Winter"],
        "occasions": ["Casual", "Office", "Travel"],
        "base_price": Decimal("1799"),
        "cost_price": Decimal("720"),
        "sizes": ["M", "L", "XL", "XXL"],
        "colors": ["Navy", "Maroon", "Grey", "Black"],
        "brand": "SK Brands",
        "material": "Wool Blend",
        "sku_prefix": "SKB-WIN-01",
        "created_at": datetime(2023, 9, 1).isoformat(),
    },
    {
        "product_id": "PROD_WIN_02",
        "product_name": "Lightweight Jacket",
        "category": "Winter Wear",
        "sub_category": "Jacket",
        "gender": "Male",
        "seasons": ["Winter", "Monsoon"],
        "occasions": ["Casual", "Travel", "Outdoor"],
        "base_price": Decimal("2499"),
        "cost_price": Decimal("1000"),
        "sizes": ["M", "L", "XL", "XXL"],
        "colors": ["Black", "Navy", "Olive"],
        "brand": "SK Brands",
        "material": "Polyester",
        "sku_prefix": "SKB-WIN-02",
        "created_at": datetime(2023, 9, 15).isoformat(),
    },
    # ========================================================================
    # WOMEN'S WEAR
    # ========================================================================
    {
        "product_id": "PROD_WMN_01",
        "product_name": "Ladies Formal Blouse",
        "category": "Women Tops",
        "sub_category": "Formal",
        "gender": "Female",
        "seasons": ["All-Season"],
        "occasions": ["Office", "Meeting", "Interview"],
        "base_price": Decimal("1199"),
        "cost_price": Decimal("480"),
        "sizes": ["XS", "S", "M", "L", "XL"],
        "colors": ["White", "Light Blue", "Pink", "Black"],
        "brand": "SK Brands",
        "material": "Polyester Blend",
        "sku_prefix": "SKB-WMN-01",
        "created_at": datetime(2023, 4, 1).isoformat(),
    },
    {
        "product_id": "PROD_WMN_02",
        "product_name": "Casual Kurti",
        "category": "Women Tops",
        "sub_category": "Kurti",
        "gender": "Female",
        "seasons": ["All-Season"],
        "occasions": ["Casual", "Office", "Festival"],
        "base_price": Decimal("899"),
        "cost_price": Decimal("360"),
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "colors": ["Red", "Blue", "Green", "Yellow", "Pink"],
        "brand": "SK Brands",
        "material": "Cotton",
        "sku_prefix": "SKB-WMN-02",
        "created_at": datetime(2023, 5, 1).isoformat(),
    },
]


def generate_products() -> list[dict[str, Any]]:
    """
    Generate product data for seeding.

    Returns:
        List of product dictionaries ready for DynamoDB insertion.
    """
    products = []
    for product in PRODUCTS_DATA:
        # Convert Decimal to float for JSON serialization if needed
        p = product.copy()
        p["base_price"] = float(p["base_price"])
        p["cost_price"] = float(p["cost_price"])
        products.append(p)
    return products


# Product characteristics for demand simulation
PRODUCT_CHARACTERISTICS: dict[str, dict[str, Any]] = {
    "PROD_SHT_F01": {"base_demand": 100, "trend_factor": 1.2, "is_trending": True},
    "PROD_SHT_F02": {"base_demand": 80, "trend_factor": 1.0, "is_trending": False},
    "PROD_SHT_F03": {"base_demand": 70, "trend_factor": 0.9, "is_trending": False},
    "PROD_SHT_C01": {"base_demand": 90, "trend_factor": 1.3, "is_trending": True},  # Summer trending
    "PROD_SHT_C02": {"base_demand": 60, "trend_factor": 0.8, "is_trending": False},
    "PROD_TSH_01": {"base_demand": 120, "trend_factor": 1.1, "is_trending": True},
    "PROD_TSH_02": {"base_demand": 150, "trend_factor": 1.0, "is_trending": False},
    "PROD_TSH_03": {"base_demand": 80, "trend_factor": 1.4, "is_trending": True},  # Youth trending
    "PROD_TRS_F01": {"base_demand": 90, "trend_factor": 1.0, "is_trending": False},
    "PROD_TRS_F02": {"base_demand": 70, "trend_factor": 1.1, "is_trending": False},
    "PROD_TRS_C01": {"base_demand": 85, "trend_factor": 1.2, "is_trending": True},
    "PROD_JNS_01": {"base_demand": 100, "trend_factor": 1.0, "is_trending": False},
    "PROD_JNS_02": {"base_demand": 75, "trend_factor": 1.3, "is_trending": True},
    "PROD_ETH_01": {"base_demand": 50, "trend_factor": 0.7, "is_trending": False},  # Seasonal
    "PROD_ETH_02": {"base_demand": 60, "trend_factor": 0.8, "is_trending": False},
    "PROD_WIN_01": {"base_demand": 40, "trend_factor": 0.5, "is_trending": False},  # Winter only
    "PROD_WIN_02": {"base_demand": 30, "trend_factor": 0.4, "is_trending": False},
    "PROD_WMN_01": {"base_demand": 70, "trend_factor": 1.1, "is_trending": False},
    "PROD_WMN_02": {"base_demand": 90, "trend_factor": 1.2, "is_trending": True},
}


def get_product_characteristic(product_id: str, characteristic: str) -> Any:
    """Get a specific characteristic value for a product."""
    return PRODUCT_CHARACTERISTICS.get(product_id, {}).get(characteristic)

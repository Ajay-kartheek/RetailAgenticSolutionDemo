"""
Tools for the Brand Campaign Agent.
"""

import sys
from pathlib import Path
from typing import Any
from datetime import datetime
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.db import DynamoDBClient
from config.settings import settings


db_client = DynamoDBClient()


def generate_campaign_image(
    product_name: str,
    campaign_type: str = "banner",
    promotion_text: str | None = None,
    occasion: str | None = None,
    style: str = "modern and professional",
) -> dict[str, Any]:
    """
    Generate a campaign image using Amazon Nova Canvas.

    Args:
        product_name: Product to feature
        campaign_type: Type of campaign (banner/social/email/whatsapp)
        promotion_text: Promotion text (e.g., "20% OFF")
        occasion: Occasion if any (e.g., "Diwali")
        style: Visual style

    Returns:
        Generated image data
    """
    try:
        from shared.bedrock import bedrock_client

        result = bedrock_client.generate_campaign_image(
            product_name=product_name,
            campaign_type=campaign_type,
            promotion_text=promotion_text,
            occasion=occasion,
            style=style,
        )

        return {
            "success": result.get("success", False),
            "image_base64": result.get("image_base64"),
            "prompt_used": result.get("prompt"),
            "dimensions": {
                "width": result.get("width"),
                "height": result.get("height"),
            },
            "campaign_type": campaign_type,
            "product_name": product_name,
            "occasion": occasion,
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "campaign_type": campaign_type,
            "product_name": product_name,
        }


def create_campaign(
    campaign_name: str,
    product_ids: list[str],
    store_ids: list[str],
    campaign_type: str = "banner",
    promotion_text: str | None = None,
    occasion: str | None = None,
    generate_image: bool = True,
) -> dict[str, Any]:
    """
    Create a complete marketing campaign.

    Args:
        campaign_name: Name for the campaign
        product_ids: Products to feature
        store_ids: Target stores
        campaign_type: Type of creative (banner/social/email/whatsapp)
        promotion_text: Promotion text
        occasion: Occasion/event
        generate_image: Whether to generate image

    Returns:
        Complete campaign details
    """
    campaign_id = f"CAMP_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6].upper()}"

    # Get product details
    products = []
    for product_id in product_ids[:3]:  # Limit to 3 products
        product = db_client.get_item(settings.products_table, {"product_id": product_id})
        if product:
            products.append({
                "product_id": product_id,
                "product_name": product.get("product_name"),
                "price": float(product.get("base_price", 0)),
            })

    # Get store details
    stores = []
    for store_id in store_ids:
        store = db_client.get_item(settings.stores_table, {"store_id": store_id})
        if store:
            stores.append({
                "store_id": store_id,
                "store_name": store.get("store_name"),
                "city": store.get("city"),
            })

    # Generate headline and CTA based on campaign type
    if promotion_text:
        headline = f"{promotion_text} on {products[0]['product_name'] if products else 'Selected Items'}"
        cta = "Shop Now"
    elif occasion:
        headline = f"{occasion} Collection - New Arrivals"
        cta = "Explore Collection"
    else:
        headline = f"Discover {products[0]['product_name'] if products else 'Premium Fashion'}"
        cta = "Shop Now"

    # Generate image if requested
    image_data = None
    if generate_image and products:
        image_data = generate_campaign_image(
            product_name=products[0]["product_name"],
            campaign_type=campaign_type,
            promotion_text=promotion_text,
            occasion=occasion,
        )

    # Estimate reach (simplified)
    base_reach = {
        "banner": 5000,
        "social": 10000,
        "email": 3000,
        "whatsapp": 2000,
    }
    estimated_reach = base_reach.get(campaign_type, 5000) * len(store_ids)
    estimated_uplift = 0.05 if promotion_text else 0.02  # 5% with promo, 2% without

    campaign = {
        "campaign_id": campaign_id,
        "campaign_name": campaign_name,
        "campaign_type": campaign_type,
        "products": products,
        "stores": stores,
        "promotion_text": promotion_text,
        "occasion": occasion,
        "headline": headline,
        "description": f"Exclusive collection at SK Brands. {promotion_text or 'Premium quality guaranteed.'}",
        "call_to_action": cta,
        "image": image_data if image_data and image_data.get("success") else None,
        "image_generation_status": "success" if image_data and image_data.get("success") else "pending",
        "estimated_reach": estimated_reach,
        "estimated_uplift_percent": estimated_uplift * 100,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
    }

    return campaign


def create_promotion_campaign(
    pricing_recommendation: dict,
) -> dict[str, Any]:
    """
    Create a campaign from a pricing/promotion recommendation.

    Args:
        pricing_recommendation: Recommendation from Pricing Agent

    Returns:
        Campaign for the promotion
    """
    store_id = pricing_recommendation.get("store_id")
    product_id = pricing_recommendation.get("product_id")
    product_name = pricing_recommendation.get("product_name", "Product")
    price_change = pricing_recommendation.get("price_change_percent", 0)
    rec_type = pricing_recommendation.get("recommendation_type", "discount")

    # Create promotion text
    if price_change < 0:
        promotion_text = f"{abs(int(price_change))}% OFF"
    elif rec_type == "flash_sale":
        promotion_text = "Flash Sale - Limited Time!"
    elif rec_type == "bundle":
        promotion_text = "Bundle & Save"
    else:
        promotion_text = "Special Offer"

    campaign_name = f"{product_name} - {promotion_text}"

    return create_campaign(
        campaign_name=campaign_name,
        product_ids=[product_id],
        store_ids=[store_id],
        campaign_type="social",
        promotion_text=promotion_text,
        generate_image=True,
    )


def get_campaign_suggestions(
    pricing_data: dict | None = None,
    trend_data: dict | None = None,
) -> dict[str, Any]:
    """
    Get campaign suggestions based on pricing and trend data.

    Args:
        pricing_data: Pricing recommendations
        trend_data: Trend analysis

    Returns:
        Suggested campaigns
    """
    suggestions = []

    # From pricing recommendations
    if pricing_data:
        recommendations = pricing_data.get("recommendations", [])
        for rec in recommendations[:5]:  # Top 5
            if rec.get("price_change_percent", 0) < -10:  # Significant discount
                pct_off = abs(int(rec.get('price_change_percent', 0)))
                suggestions.append({
                    "campaign_id": f"SUG_{uuid.uuid4().hex[:6].upper()}",
                    "type": "Clearance Sale",
                    "trigger": "Pricing Optimization",
                    "products": [rec.get("product_name", rec.get("product_id"))],
                    "product_id": rec.get("product_id"),
                    "store_id": rec.get("store_id"),
                    "promotion_text": f"{pct_off}% OFF",
                    "reason": rec.get("reasoning", "Optimizing inventory turnover"),
                    "suggested_action": f"Run {pct_off}% OFF Clearance on {rec.get('product_name')}",
                    "expected_impact": "high",
                    "priority": "high",
                })

    # From trending products
    if trend_data:
        trending = trend_data.get("trending_products", [])
        for item in trending[:3]:  # Top 3 trending
            suggestions.append({
                "campaign_id": f"SUG_{uuid.uuid4().hex[:6].upper()}",
                "type": "Trending Now",
                "trigger": "Market Trend",
                "products": [item.get("product_name", item.get("product_id"))],
                "product_id": item.get("product_id"),
                "store_id": item.get("store_id"),
                "promotion_text": "Trending Item",
                "reason": f"Trending with {item.get('velocity_ratio', 0):.1f}x velocity",
                "suggested_action": f"Feature {item.get('product_name')} in 'Trending' Collection",
                "expected_impact": "medium",
                "priority": "medium",
            })
            
    # Allow for mock suggestions if no data provided (for demo purposes)
    if not suggestions and not pricing_data and not trend_data:
        suggestions = [
             {
                "campaign_id": "SUG_DEMO_01",
                "type": "Clearance Sale",
                "trigger": "Overstock Analysis",
                "products": ["Winter Jacket"],
                "reason": "High inventory levels detected in Chennai store. Clear stock before summer.",
                "suggested_action": "Run End-of-Season Sale (30% OFF)",
                "expected_impact": "High ($12k revenue)",
                "priority": "high"
            },
            {
                "campaign_id": "SUG_DEMO_02",
                "type": "New Arrival",
                "trigger": "Market Trend",
                "products": ["Summer Cotton Shirt"],
                "reason": "Rising demand for cotton apparel in southern region.",
                "suggested_action": "Launch 'Summer Essentials' Email Campaign",
                "expected_impact": "Medium ($5k revenue)",
                "priority": "medium"
            }
        ]

    return {
        "total_suggestions": len(suggestions),
        "suggestions": suggestions,
        "generated_at": datetime.utcnow().isoformat(),
    }


CAMPAIGN_TOOLS = [
    {
        "name": "generate_campaign_image",
        "description": "Generate a marketing image using AI",
        "function": generate_campaign_image,
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {"type": "string"},
                "campaign_type": {"type": "string", "enum": ["banner", "social", "email", "whatsapp"]},
                "promotion_text": {"type": "string"},
                "occasion": {"type": "string"},
                "style": {"type": "string"},
            },
            "required": ["product_name"],
        },
    },
    {
        "name": "create_campaign",
        "description": "Create a complete marketing campaign",
        "function": create_campaign,
        "parameters": {
            "type": "object",
            "properties": {
                "campaign_name": {"type": "string"},
                "product_ids": {"type": "array", "items": {"type": "string"}},
                "store_ids": {"type": "array", "items": {"type": "string"}},
                "campaign_type": {"type": "string"},
                "promotion_text": {"type": "string"},
                "occasion": {"type": "string"},
                "generate_image": {"type": "boolean"},
            },
            "required": ["campaign_name", "product_ids", "store_ids"],
        },
    },
    {
        "name": "get_campaign_suggestions",
        "description": "Get campaign suggestions from pricing and trend data",
        "function": get_campaign_suggestions,
        "parameters": {
            "type": "object",
            "properties": {
                "pricing_data": {"type": "object"},
                "trend_data": {"type": "object"},
            },
            "required": [],
        },
    },
]

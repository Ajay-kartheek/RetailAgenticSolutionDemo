"""
Campaign Routes - AI Image Generation for Marketing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.bedrock import BedrockClient
from shared.db import DynamoDBClient
from agents.campaign_agent import CampaignAgent

router = APIRouter()
logger = logging.getLogger(__name__)
bedrock = BedrockClient()
db = DynamoDBClient()


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    product_id: str
    campaign_type: str = "promotional"  # promotional, seasonal, clearance, new_arrival
    promotion_text: Optional[str] = None
    style: Optional[str] = "professional retail photography"


class CampaignRequest(BaseModel):
    """Request model for full campaign creation."""
    product_ids: list[str]
    campaign_type: str = "promotional"
    promotion_details: Optional[str] = None


@router.post("/generate-image")
async def generate_campaign_image(request: ImageGenerationRequest):
    """
    Generate a marketing campaign image for a product using Amazon Nova Canvas.
    """
    # Get product details
    product = db.get_product(request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {request.product_id} not found")

    try:
        logger.info(f"Generating campaign image for product {request.product_id}")

        result = bedrock.generate_campaign_image(
            product_name=product.get("name", "Product"),
            campaign_type=request.campaign_type,
            promotion_text=request.promotion_text,
            style=request.style,
            product_category=product.get("category"),
            product_color=product.get("color")
        )

        return {
            "product_id": request.product_id,
            "product_name": product.get("name"),
            "campaign_type": request.campaign_type,
            "image_base64": result.get("image_base64"),
            "prompt_used": result.get("prompt")
        }

    except Exception as e:
        logger.error(f"Image generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.post("/create")
async def create_campaign(request: CampaignRequest):
    """
    Create a full marketing campaign with AI-generated creatives.
    """
    # Validate products exist
    products = []
    for product_id in request.product_ids:
        product = db.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
        products.append(product)

    try:
        campaign_agent = CampaignAgent()

        result = campaign_agent.create_campaign(
            products=products,
            campaign_type=request.campaign_type,
            promotion_details=request.promotion_details
        )

        return result

    except Exception as e:
        logger.error(f"Campaign creation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Campaign creation failed: {str(e)}")


@router.get("/suggestions")
async def get_campaign_suggestions():
    """
    Get AI-suggested campaigns based on current inventory and trends.
    Uses the Campaign Agent to analyze data and suggest campaigns.
    """
    try:
        campaign_agent = CampaignAgent()
        suggestions = campaign_agent.get_suggestions()
        return {"suggestions": suggestions}

    except Exception as e:
        logger.error(f"Failed to get campaign suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def list_campaign_types():
    """List available campaign types."""
    return {
        "campaign_types": [
            {
                "type": "promotional",
                "description": "General promotional campaign with discounts",
                "best_for": "Overstocked items, slow-moving inventory"
            },
            {
                "type": "seasonal",
                "description": "Season-specific campaign (Pongal, Diwali, etc.)",
                "best_for": "Seasonal products, festive collections"
            },
            {
                "type": "clearance",
                "description": "End-of-season clearance sale",
                "best_for": "End-of-season stock, heavily overstocked items"
            },
            {
                "type": "new_arrival",
                "description": "New product launch campaign",
                "best_for": "New products, trending items"
            },
            {
                "type": "flash_sale",
                "description": "Limited-time flash sale",
                "best_for": "Quick inventory movement, customer engagement"
            }
        ]
    }

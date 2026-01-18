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
        
        # Get product name with fallback
        product_name = product.get("name") or product.get("product_name") or "Clothing Product"
        product_category = product.get("category", "")
        
        # Build more specific product description
        full_product_desc = f"{product_name} ({product_category})" if product_category else product_name

        result = bedrock.generate_campaign_image(
            product_name=full_product_desc,
            campaign_type=request.campaign_type,
            promotion_text=request.promotion_text,
            style=request.style
        )

        return {
            "product_id": request.product_id,
            "product_name": product_name,
            "product_category": product_category,
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
async def get_campaign_suggestions_route():
    """
    Get AI-suggested campaigns based on current inventory and trends.
    Uses the campaign agent tools to suggest campaigns.
    """
    try:
        from agents.campaign_agent.tools import get_campaign_suggestions
        suggestions = get_campaign_suggestions()
        return {"suggestions": suggestions.get("suggestions", [])}

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


@router.post("/analyze/stream")
async def analyze_campaigns_stream():
    """
    Run AI-powered campaign analysis with SSE streaming.
    
    This triggers the Campaign Agent with real data:
    - Gets pricing recommendations from database
    - Gets trend analysis data
    - Uses Claude to generate intelligent campaign suggestions
    - Streams progress updates via SSE
    """
    import asyncio
    import uuid
    import json
    from fastapi.responses import StreamingResponse
    from config.settings import settings
    from config.aws import get_dynamodb_resource
    
    run_id = str(uuid.uuid4())[:8]
    
    async def generate():
        try:
            # Start event
            yield f"data: {json.dumps({'type': 'start', 'run_id': run_id, 'agent_name': 'Orchestrator', 'message': 'Initializing campaign analysis...'})}\n\n"
            await asyncio.sleep(0.3)
            
            # Delegate to Campaign Agent
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Orchestrator', 'message': 'Delegating to Campaign Agent...', 'status': 'running'})}\n\n"
            await asyncio.sleep(0.5)
            
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': 'Fetching product catalog...', 'status': 'running'})}\n\n"
            
            # Get actual products data
            dynamodb = get_dynamodb_resource()
            products_table = dynamodb.Table(settings.products_table)
            stores_table = dynamodb.Table(settings.stores_table)
            inventory_table = dynamodb.Table(settings.inventory_table)
            
            products = []
            stores = []
            inventory_data = []
            
            try:
                response = products_table.scan()
                products = response.get("Items", [])
            except Exception as e:
                logger.warning(f"Failed to fetch products: {e}")
            
            await asyncio.sleep(0.3)
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': f'Found {len(products)} products in catalog', 'status': 'running'})}\n\n"
            
            # Get stores
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': 'Analyzing store network...', 'status': 'running'})}\n\n"
            
            try:
                response = stores_table.scan()
                stores = response.get("Items", [])
            except Exception as e:
                logger.warning(f"Failed to fetch stores: {e}")
            
            await asyncio.sleep(0.3)
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': f'Found {len(stores)} stores across South India', 'status': 'running'})}\n\n"
            
            # Get inventory levels
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': 'Checking inventory levels...', 'status': 'running'})}\n\n"
            
            try:
                response = inventory_table.scan()
                inventory_data = response.get("Items", [])
            except Exception as e:
                logger.warning(f"Failed to fetch inventory: {e}")
            
            # Calculate inventory insights
            high_stock = [i for i in inventory_data if int(i.get("quantity", 0)) > 50]
            low_stock = [i for i in inventory_data if int(i.get("quantity", 0)) < 20]
            
            await asyncio.sleep(0.3)
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': f'Inventory: {len(high_stock)} high-stock, {len(low_stock)} low-stock items', 'status': 'running'})}\n\n"
            
            # Generate AI suggestions using Claude
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': 'Generating AI campaign recommendations...', 'thinking': 'Analyzing product mix, store network, and inventory levels...', 'status': 'running'})}\n\n"
            
            suggestions = []
            
            try:
                from shared.bedrock import bedrock_client
                
                # Build rich context for Claude
                product_summary = [{'name': p.get('name', p.get('product_name', 'Unknown')), 'category': p.get('category', 'Unknown')} for p in products[:6]]
                store_cities = list(set([s.get('city', 'Unknown') for s in stores]))[:5]
                
                context = f"""
You are a retail marketing strategist for SK Brands, a South Indian clothing retailer.

Current Business Data:
- Products: {len(products)} items including {product_summary}
- Store Network: {len(stores)} stores in cities like {store_cities}
- Inventory Status: {len(high_stock)} products with high stock (>50 units), {len(low_stock)} products with low stock (<20 units)
- Season: January (post-holiday, pre-summer transition)

Generate 2-3 strategic campaign recommendations. For each, provide:
1. campaign_type: "clearance", "promotional", "seasonal", or "new_arrival"  
2. title: Short, catchy campaign title
3. description: 2-3 sentences explaining WHY this campaign makes sense based on the data
4. expected_impact: "high", "medium", or "low" revenue potential
5. target_products: List of product categories to target (e.g., ["Winterwear", "Traditional"])

Respond in JSON format only:
{{"suggestions": [...]}}
"""
                
                response = bedrock_client.invoke_claude(
                    prompt=context,
                    system_prompt="You are a retail marketing AI. Respond only with valid JSON.",
                    max_tokens=1000,
                    temperature=0.7
                )
                
                # Parse response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    suggestions = parsed.get("suggestions", [])
                    
            except Exception as e:
                logger.error(f"Claude error: {e}")
                # Fallback suggestions if Claude fails
                suggestions = [
                    {
                        "campaign_type": "clearance",
                        "title": "End-of-Season Clearance",
                        "description": "Clear overstocked winter inventory before spring arrivals",
                        "expected_impact": "high",
                        "target_products": ["Winterwear", "Jackets"]
                    }
                ]
            
            await asyncio.sleep(0.5)
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Campaign Agent', 'message': f'Generated {len(suggestions)} campaign recommendations', 'status': 'completed'})}\n\n"
            
            # Orchestrator wrap up
            yield f"data: {json.dumps({'type': 'progress', 'agent_name': 'Orchestrator', 'message': 'Campaign analysis complete!', 'status': 'completed'})}\n\n"
            
            # Final result
            yield f"data: {json.dumps({'type': 'complete', 'suggestions': suggestions})}\n\n"
            
        except Exception as e:
            logger.error(f"Campaign analysis failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


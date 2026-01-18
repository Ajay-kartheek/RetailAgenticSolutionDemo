"""
Trends Routes - Fetch Trend Analysis Data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.db import DynamoDBClient
from config.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)
db = DynamoDBClient()


class TrendAnalysis(BaseModel):
    """Model for trend analysis data."""
    store_product_id: str
    analysis_date: str
    trend_name: str
    confidence_score: float
    impact_score: float
    affected_products: List[str]
    description: str
    action_item: Optional[str] = None


@router.get("/")
async def get_trends():
    """
    Fetch recent trend analysis data.
    """
    try:
        # In a real app, we would query the sk_trend_analysis table
        # For now, we'll scan the table or fetch mock data if empty
        
        # Using the low-level dynamodb resource to scan (simple for demo)
        from config.aws import get_dynamodb_resource
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(settings.trend_analysis_table)
        
        response = table.scan()
        items = response.get("Items", [])
        
        # Sort by date descending
        items.sort(key=lambda x: x.get("analysis_date", ""), reverse=True)
        
        return {"trends": items}

    except Exception as e:
        logger.error(f"Failed to fetch trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

"""
Activity Routes - Agent activity logs API
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter

from config.settings import settings
from shared.db import DynamoDBClient

router = APIRouter()
db = DynamoDBClient()


@router.get("/")
async def list_activities(
    agent_id: Optional[str] = None,
    limit: int = 50
):
    """Get recent agent activities."""
    try:
        # Scan the activity table
        activities = db.scan(settings.agent_activity_table)
        
        # Filter by agent if specified
        if agent_id:
            activities = [a for a in activities if a.get("agent_id") == agent_id]
        
        # Sort by timestamp descending (most recent first)
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Limit results
        activities = activities[:limit]
        
        return {
            "activities": activities,
            "count": len(activities)
        }
    except Exception as e:
        return {
            "activities": [],
            "count": 0,
            "error": str(e)
        }


@router.get("/recent")
async def get_recent_activities(limit: int = 10):
    """Get the most recent activities across all agents."""
    try:
        activities = db.scan(settings.agent_activity_table)
        
        # Sort by timestamp descending
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "activities": activities[:limit],
            "count": min(len(activities), limit)
        }
    except Exception as e:
        return {
            "activities": [],
            "count": 0,
            "error": str(e)
        }


@router.get("/by-agent/{agent_id}")
async def get_agent_activities(agent_id: str, limit: int = 20):
    """Get activities for a specific agent."""
    try:
        # Scan and filter
        activities = db.scan(settings.agent_activity_table)
        activities = [a for a in activities if a.get("agent_id") == agent_id]
        activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "agent_id": agent_id,
            "activities": activities[:limit],
            "count": len(activities[:limit])
        }
    except Exception as e:
        return {
            "agent_id": agent_id,
            "activities": [],
            "count": 0,
            "error": str(e)
        }

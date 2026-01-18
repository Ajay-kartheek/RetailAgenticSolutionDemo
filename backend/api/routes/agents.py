"""
Agents API routes.
"""

from fastapi import APIRouter
from boto3.dynamodb.conditions import Key
import logging

from shared.db import DynamoDBClient
from config.settings import settings

router = APIRouter(prefix="/agents", tags=["agents"])
logger = logging.getLogger(__name__)

@router.get("/history")
async def get_agents_history():
    """
    Get the latest run results for all agents.
    Returns the most recent analysis for each agent type.
    """
    db = DynamoDBClient()
    table_name = settings.agent_runs_table
    
    # We want the LATEST run for each agent.
    # Since we don't have a single "latest run ID" easily accessible without querying,
    # we can query by agent_id using the GSI (agent-timestamp-index) to get the latest.
    
    agent_types = [
        "Orchestrator",
        "demand_agent", 
        "trend_agent", 
        "inventory_agent", 
        "replenishment_agent", 
        "pricing_agent", 
        "campaign_agent"
    ]
    
    history = {}
    
    try:
        for agent_id in agent_types:
            # query GSI: agent_id = :agent_id, scan_index_forward=False (descending) limit 1
            response = db.query(
                table_name=table_name,
                key_condition=Key('agent_id').eq(agent_id),
                limit=1,
                ScanIndexForward=False, # Get latest first
                index_name="agent-timestamp-index"
            )
            
            if response:
                history[agent_id] = response[0]
            else:
                # Return empty struct if no history yet
                history[agent_id] = {
                    "agent_id": agent_id,
                    "summary": "No analysis history available yet.",
                    "insights": [],
                    "recommendations": [],
                    "metrics": {}
                }
                
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Error fetching agent history: {e}")
        return {"error": str(e), "history": {}}

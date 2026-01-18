"""
SK Brands Retail Agentic AI - Agent Module

This module contains all the AI agents for the retail intelligence platform:
- Orchestrator Agent: Coordinates all other agents
- Demand Agent: Analyzes demand forecasts
- Trend Agent: Analyzes sales trends and velocity
- Inventory Agent: Analyzes inventory status
- Replenishment Agent: Plans stock replenishment
- Pricing Agent: Recommends pricing and promotions
- Campaign Agent: Generates marketing campaigns
"""

from .orchestrator.agent import create_orchestrator_agent
from .demand_agent.agent import create_demand_agent
from .trend_agent.agent import create_trend_agent
from .inventory_agent.agent import create_inventory_agent
from .replenishment_agent.agent import create_replenishment_agent
from .pricing_agent.agent import create_pricing_agent
from .campaign_agent.agent import create_campaign_agent

__all__ = [
    "create_orchestrator_agent",
    "create_demand_agent",
    "create_trend_agent",
    "create_inventory_agent",
    "create_replenishment_agent",
    "create_pricing_agent",
    "create_campaign_agent",
]

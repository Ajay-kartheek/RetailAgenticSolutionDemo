"""
Brand Campaign Agent for SK Brands Retail.
"""

from typing import Any
from datetime import datetime

from .prompts import CAMPAIGN_AGENT_SYSTEM_PROMPT
from .tools import (
    generate_campaign_image,
    create_campaign,
    get_campaign_suggestions,
    create_promotion_campaign,
    CAMPAIGN_TOOLS,
)


class CampaignAgent:
    """Campaign Agent that generates marketing campaigns and creatives."""

    def __init__(self, bedrock_client: Any = None):
        self.name = "Brand Campaign Agent"
        self.agent_id = "campaign_agent"
        self.system_prompt = CAMPAIGN_AGENT_SYSTEM_PROMPT

        if bedrock_client is None:
            from shared.bedrock import bedrock_client as default_client
            self.bedrock_client = default_client
        else:
            self.bedrock_client = bedrock_client

        self.tools = {
            "generate_campaign_image": generate_campaign_image,
            "create_campaign": create_campaign,
            "get_campaign_suggestions": get_campaign_suggestions,
            "create_promotion_campaign": create_promotion_campaign,
        }
        self.tool_definitions = CAMPAIGN_TOOLS

    def analyze(
        self,
        pricing_data: dict[str, Any] | None = None,
        trend_data: dict[str, Any] | None = None,
        user_request: str | None = None,
        generate_images: bool = False,
    ) -> dict[str, Any]:
        """
        Generate campaign suggestions and optionally create campaigns.

        Args:
            pricing_data: Pricing recommendations from Pricing Agent
            trend_data: Trend analysis from Trend Agent
            user_request: Optional specific campaign request
            generate_images: Whether to generate images for campaigns

        Returns:
            Campaign suggestions and any generated campaigns
        """
        results = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": [],
            "generated_campaigns": [],
            "insights": [],
        }

        # Get suggestions
        suggestions = get_campaign_suggestions(
            pricing_data=pricing_data,
            trend_data=trend_data,
        )
        results["suggestions"] = suggestions.get("suggestions", [])

        # Generate campaigns for high priority suggestions if requested
        if generate_images:
            high_priority = [s for s in results["suggestions"] if s.get("priority") == "high"]
            for suggestion in high_priority[:2]:  # Limit to 2 for demo
                if suggestion.get("type") == "promotion" and pricing_data:
                    # Find the matching pricing recommendation
                    recs = pricing_data.get("recommendations", [])
                    matching_rec = next(
                        (r for r in recs if r.get("product_id") == suggestion.get("product_id")),
                        None
                    )
                    if matching_rec:
                        campaign = create_promotion_campaign(matching_rec)
                        results["generated_campaigns"].append(campaign)

        # Generate insights
        results["insights"] = self._generate_insights(results)

        return results

    def generate_custom_campaign(
        self,
        campaign_name: str,
        product_ids: list[str],
        store_ids: list[str],
        campaign_type: str = "social",
        promotion_text: str | None = None,
        occasion: str | None = None,
    ) -> dict[str, Any]:
        """Generate a custom campaign based on user request."""
        campaign = create_campaign(
            campaign_name=campaign_name,
            product_ids=product_ids,
            store_ids=store_ids,
            campaign_type=campaign_type,
            promotion_text=promotion_text,
            occasion=occasion,
            generate_image=True,
        )

        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "campaign": campaign,
        }

    def _generate_insights(self, data: dict) -> list[str]:
        insights = []
        suggestions = data.get("suggestions", [])
        campaigns = data.get("generated_campaigns", [])

        high_priority = len([s for s in suggestions if s.get("priority") == "high"])
        if high_priority:
            insights.append(f"{high_priority} high-priority campaign opportunities identified")

        if campaigns:
            insights.append(f"{len(campaigns)} campaign creatives generated")

        return insights

    def as_tool(self) -> dict:
        return {
            "name": "campaign_agent",
            "description": (
                "Generate marketing campaign suggestions and creatives. "
                "Can create banner, social, email, and WhatsApp campaigns with AI-generated images."
            ),
            "function": self.analyze,
            "parameters": {
                "type": "object",
                "properties": {
                    "pricing_data": {"type": "object"},
                    "trend_data": {"type": "object"},
                    "user_request": {"type": "string"},
                    "generate_images": {"type": "boolean", "default": False},
                },
                "required": [],
            },
        }


def create_campaign_agent(bedrock_client: Any = None) -> CampaignAgent:
    return CampaignAgent(bedrock_client=bedrock_client)

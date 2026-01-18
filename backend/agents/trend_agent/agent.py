"""
Trend Analyser Agent for SK Brands Retail.

This agent analyzes sales velocity against demand forecasts to
classify products as in-trend, average, slow-moving, or no-trend.
"""

import json
from typing import Any
from datetime import datetime, date

from .prompts import TREND_AGENT_SYSTEM_PROMPT, TREND_AGENT_TASK_PROMPT
from .tools import (
    analyze_sales_trend,
    get_trending_products,
    get_slow_moving_products,
    TREND_TOOLS,
)


class TrendAgent:
    """
    Trend Analyser Agent that compares actual sales against forecasts.

    This agent calculates velocity ratios and classifies products into
    trend categories to identify which items are performing above or
    below expectations.
    """

    def __init__(self, bedrock_client: Any = None):
        """
        Initialize the Trend Agent.

        Args:
            bedrock_client: Optional Bedrock client for LLM calls.
        """
        self.name = "Trend Analyser Agent"
        self.agent_id = "trend_agent"
        self.system_prompt = TREND_AGENT_SYSTEM_PROMPT

        if bedrock_client is None:
            from shared.bedrock import bedrock_client as default_client
            self.bedrock_client = default_client
        else:
            self.bedrock_client = bedrock_client

        # Register tools
        self.tools = {
            "analyze_sales_trend": analyze_sales_trend,
            "get_trending_products": get_trending_products,
            "get_slow_moving_products": get_slow_moving_products,
        }

        self.tool_definitions = TREND_TOOLS

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a tool by name with given input."""
        if tool_name not in self.tools:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**tool_input)
            return result
        except Exception as e:
            return {"error": str(e)}

    def analyze(
        self,
        demand_data: dict[str, Any] | None = None,
        forecast_period: str = "2026-Q1",
        store_ids: list[str] | None = None,
        product_ids: list[str] | None = None,
        as_of_date: str | None = None,
    ) -> dict[str, Any]:
        """
        Run trend analysis.

        Args:
            demand_data: Optional demand data from Demand Agent
            forecast_period: Forecast period to analyze
            store_ids: Optional list of specific stores to analyze
            product_ids: Optional list of specific products to analyze
            as_of_date: Analysis date (defaults to today)

        Returns:
            Trend analysis results with classifications
        """
        analysis_date = as_of_date or date.today().isoformat()

        results = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "analysis_date": analysis_date,
            "forecast_period": forecast_period,
            "trending_products": [],
            "average_products": [],
            "slow_moving_products": [],
            "no_trend_products": [],
            "summary": {},
            "insights": [],
            "recommendations": [],
        }

        # Get REAL trend data from DynamoDB (limited to top 5 for performance)
        trending_data = get_trending_products(
            forecast_period=forecast_period,
            min_velocity_ratio=1.5,
            as_of_date=analysis_date,
        )

        slow_data = get_slow_moving_products(
            forecast_period=forecast_period,
            max_velocity_ratio=0.8,
            as_of_date=analysis_date,
        )

        trending_products = trending_data.get("trending_products", [])[:5]
        slow_products = slow_data.get("slow_moving_products", [])[:5]

        # Build task for LLM to analyze REAL data
        task = f"""Analyze sales trend data for SK Brands retail stores for period {forecast_period}.

**Trending Products (selling faster than expected):**
{json.dumps(trending_products, indent=2)}

**Slow-Moving Products (underperforming):**
{json.dumps(slow_products, indent=2)}

**Context:** Velocity ratio compares actual sales to forecasted demand. Ratio > 1.5 = trending, < 0.8 = slow-moving.

Provide:
1. Key insights about trending vs slow-moving patterns
2. Store-level observations
3. Actionable recommendations for inventory and pricing teams
"""

        # Call LLM for analysis
        try:
            llm_response = self.bedrock_client.invoke_claude(
                prompt=task,
                system_prompt=self.system_prompt,
                max_tokens=2048,
                temperature=0.7
            )

            results["llm_analysis"] = llm_response
            results["trending_products"] = trending_products
            results["slow_moving_products"] = slow_products
            results["insights"] = self._extract_insights_from_llm(llm_response)
            results["recommendations"] = self._extract_recommendations_from_llm(llm_response)

        except Exception as e:
            results["error"] = str(e)
            results["insights"] = [f"Error during LLM analysis: {str(e)}"]
            results["recommendations"] = []

        return results

    def _generate_insights(self, data: dict) -> list[str]:
        """Generate insights from trend analysis."""
        insights = []

        trending = data.get("trending_products", [])
        slow = data.get("slow_moving_products", [])
        no_trend = data.get("no_trend_products", [])

        # Trending insights
        if trending:
            top_trending = trending[0] if trending else None
            if top_trending:
                insights.append(
                    f"Top trending: {top_trending.get('product_name', top_trending.get('product_id'))} "
                    f"at {top_trending.get('store_id')} with {top_trending.get('velocity_ratio', 0):.1f}x velocity"
                )
            insights.append(f"{len(trending)} products are selling faster than expected")

        # Slow-moving insights
        if slow or no_trend:
            total_underperforming = len(slow) + len(no_trend)
            insights.append(f"{total_underperforming} products are underperforming vs forecast")

        # Store patterns
        summary = data.get("summary", {})
        trending_by_store = summary.get("trending_by_store", {})
        slow_by_store = summary.get("slow_by_store", {})

        if trending_by_store:
            top_store = max(trending_by_store.items(), key=lambda x: x[1])
            insights.append(f"Most trending products at {top_store[0]} ({top_store[1]} items)")

        if slow_by_store:
            worst_store = max(slow_by_store.items(), key=lambda x: x[1])
            insights.append(f"Most slow-moving products at {worst_store[0]} ({worst_store[1]} items)")

        return insights

    def _extract_insights_from_llm(self, llm_text: str) -> list[str]:
        """Extract insights from Claude's text response."""
        insights = []
        lines = llm_text.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("•"):
                insight = line[1:].strip()
                if len(insight) > 20:
                    insights.append(insight)

        return insights[:5] if insights else [llm_text[:200]]

    def _extract_recommendations_from_llm(self, llm_text: str) -> list[str]:
        """Extract recommendations from Claude's text response."""
        recommendations = []
        lines = llm_text.split("\n")

        in_rec_section = False
        for line in lines:
            line = line.strip()
            if "recommendation" in line.lower():
                in_rec_section = True
                continue
            if in_rec_section and (line.startswith("-") or line.startswith("•")):
                rec = line[1:].strip()
                if len(rec) > 20:
                    recommendations.append(rec)

        return recommendations[:5] if recommendations else []

    def _generate_recommendations(self, data: dict) -> list[str]:
        """Generate recommendations from trend analysis."""
        recommendations = []

        trending = data.get("trending_products", [])
        slow = data.get("slow_moving_products", [])
        no_trend = data.get("no_trend_products", [])

        # Trending recommendations
        if trending:
            recommendations.append(
                "Prioritize restocking in-trend items to avoid stockouts"
            )
            # Check if any trending items are at risk
            high_velocity = [t for t in trending if t.get("velocity_ratio", 0) > 2.0]
            if high_velocity:
                recommendations.append(
                    f"URGENT: {len(high_velocity)} items selling 2x+ faster than expected - check inventory levels"
                )

        # Slow-moving recommendations
        if slow:
            recommendations.append(
                f"Consider promotions for {len(slow)} slow-moving items to accelerate sales"
            )

        # No-trend recommendations
        if no_trend:
            recommendations.append(
                f"Evaluate {len(no_trend)} no-trend items for markdown or redistribution"
            )

        # Store-specific recommendations
        summary = data.get("summary", {})
        slow_by_store = summary.get("slow_by_store", {})

        # Find stores with many slow items
        problem_stores = [
            store for store, count in slow_by_store.items()
            if count > 3
        ]
        if problem_stores:
            recommendations.append(
                f"Review inventory strategy for stores with multiple slow items: {', '.join(problem_stores)}"
            )

        return recommendations

    def as_tool(self) -> dict:
        """Return this agent as a tool definition for the orchestrator."""
        return {
            "name": "trend_agent",
            "description": (
                "Analyze sales trends by comparing actual sales against demand forecasts. "
                "Identifies in-trend, average, slow-moving, and no-trend products with velocity metrics."
            ),
            "function": self.analyze,
            "parameters": {
                "type": "object",
                "properties": {
                    "demand_data": {
                        "type": "object",
                        "description": "Optional demand data from Demand Agent",
                    },
                    "forecast_period": {
                        "type": "string",
                        "description": "Forecast period to analyze (e.g., '2026-Q1')",
                        "default": "2026-Q1",
                    },
                    "store_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of specific store IDs to analyze",
                    },
                    "product_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of specific product IDs to analyze",
                    },
                    "as_of_date": {
                        "type": "string",
                        "description": "Analysis date in ISO format",
                    },
                },
                "required": [],
            },
        }


def create_trend_agent(bedrock_client: Any = None) -> TrendAgent:
    """Factory function to create a Trend Agent instance."""
    return TrendAgent(bedrock_client=bedrock_client)

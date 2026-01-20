"""
Inventory Agent for SK Brands Retail.

This agent analyzes inventory levels against demand and trend data
to identify understocked and overstocked items.
"""

import json
from typing import Any
from datetime import datetime

from .prompts import INVENTORY_AGENT_SYSTEM_PROMPT
from .tools import (
    analyze_inventory_status,
    search_inventory_items,
    INVENTORY_TOOLS,
)


class InventoryAgent:
    """Inventory Agent that analyzes stock levels and classifies inventory status."""

    def __init__(self, bedrock_client: Any = None):
        self.name = "Inventory Agent"
        self.agent_id = "inventory_agent"
        self.system_prompt = INVENTORY_AGENT_SYSTEM_PROMPT

        if bedrock_client is None:
            from shared.bedrock import bedrock_client as default_client
            self.bedrock_client = default_client
        else:
            self.bedrock_client = bedrock_client

        self.tools = {
            "analyze_inventory_status": analyze_inventory_status,
            "search_inventory_items": search_inventory_items,
        }
        self.tool_definitions = INVENTORY_TOOLS

    def analyze(
        self,
        trend_data: dict[str, Any] | None = None,
        forecast_period: str = "2026-Q1",
        store_ids: list[str] | None = None,
        product_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Run inventory analysis (Agentic Flow).
        
        The Agent will:
        1. Receive trend context
        2. Decide which tools to call (e.g. search for understocked items)
        3. Analyze the tool outputs
        4. Provide final insights
        """
        results = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "forecast_period": forecast_period,
            "insights": [],
            "recommendations": [],
        }

        # 1. Prepare Initial Context
        trend_summary = json.dumps(trend_data.get("summary", {}) if trend_data else {}, indent=2)
        
        user_message = f"""Analyze inventory for period {forecast_period}.
        
        Context from Trend Agent:
        {trend_summary}
        
        Please identify critical inventory issues (understocked < 20%, overstocked > 130%) and provide recommendations.
        """

        messages = [{"role": "user", "content": [{"text": user_message}]}]

        # 2. Agentic Loop (Max 3 turns to prevent infinite loops)
        final_response_text = ""
        
        try:
            # We use the raw converse API to handle the multi-turn flow
            for _ in range(3):
                response = self.bedrock_client.converse(
                    modelId=self.bedrock_client.model_id,
                    messages=messages,
                    system=[{"text": self.system_prompt}],
                    toolConfig={
                        "tools": [{"toolSpec": t} for t in self.tool_definitions]
                    }
                )
                
                output_message = response["output"]["message"]
                messages.append(output_message)
                
                # Check if tool use is requested
                content_blocks = output_message["content"]
                tool_requests = [block["toolUse"] for block in content_blocks if "toolUse" in block]
                
                if not tool_requests:
                    # Final text response
                    text_blocks = [b["text"] for b in content_blocks if "text" in b]
                    final_response_text = "\n".join(text_blocks)
                    break
                
                # Execute Tools
                tool_results = []
                found_data = {"understocked": [], "overstocked": []} # Capture for structured output
                
                for tool_req in tool_requests:
                    tool_name = tool_req["name"]
                    tool_args = tool_req["input"]
                    tool_use_id = tool_req["toolUseId"]
                    
                    # Execute
                    if tool_name in self.tools:
                        func = self.tools[tool_name]
                        # Inject default args if missing
                        if "forecast_period" not in tool_args:
                            tool_args["forecast_period"] = forecast_period
                            
                        result = func(**tool_args)
                        
                        # Capture structured data for frontend
                        if isinstance(result, dict) and "items" in result:
                            if tool_args.get("max_stock_ratio", 999) < 1.0:
                                found_data["understocked"].extend(result["items"])
                            elif tool_args.get("min_stock_ratio", 0) > 1.0:
                                found_data["overstocked"].extend(result["items"])
                        
                        tool_results.append({
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"json": result}]
                            }
                        })
                    else:
                        tool_results.append({
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"text": f"Error: Tool {tool_name} not found"}]
                            }
                        })
                
                # Add tool results to history
                messages.append({"role": "user", "content": tool_results})
                
                # Update results with captured data
                if found_data["understocked"]:
                    results["understocked_items"] = found_data["understocked"][:50]
                    results["critical_items"] = found_data["understocked"][:20]
                if found_data["overstocked"]:
                    results["overstocked_items"] = found_data["overstocked"][:50]

            # Parse Final Response
            results["insights"] = self._extract_insights_from_llm(final_response_text)
            results["recommendations"] = self._extract_recommendations_from_llm(final_response_text)
            
        except Exception as e:
            results["error"] = str(e)
            results["insights"] = [f"Error during agentic analysis: {str(e)}"]

        return results

    def _extract_insights_from_llm(self, llm_text: str) -> list[str]:
        """Extract insights from Claude's text response."""
        insights = []
        lines = llm_text.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith("-") or line.startswith("•") or line.startswith("*"):
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
            if in_rec_section and (line.startswith("-") or line.startswith("•") or line.startswith("*")):
                rec = line[1:].strip()
                if len(rec) > 20:
                    recommendations.append(rec)

        return recommendations[:5] if recommendations else []

    def _generate_insights(self, data: dict) -> list[str]:
        insights = []
        critical = data.get("critical_items", [])
        understocked = data.get("understocked_items", [])
        overstocked = data.get("overstocked_items", [])

        if critical:
            insights.append(f"CRITICAL: {len(critical)} items need immediate restocking")
        if understocked:
            insights.append(f"{len(understocked)} total items are understocked")
        if overstocked:
            insights.append(f"{len(overstocked)} items have excess inventory")

        return insights

    def _generate_recommendations(self, data: dict) -> list[str]:
        recommendations = []
        critical = data.get("critical_items", [])
        overstocked = data.get("overstocked_items", [])

        if critical:
            recommendations.append("Initiate emergency replenishment for critical items")
        if overstocked:
            recommendations.append("Evaluate overstocked items for transfers or promotions")

        return recommendations

    def as_tool(self) -> dict:
        return {
            "name": "inventory_agent",
            "description": (
                "Analyze inventory levels to identify understocked and overstocked items. "
                "Returns stock status classifications with urgency scores."
            ),
            "function": self.analyze,
            "parameters": {
                "type": "object",
                "properties": {
                    "trend_data": {"type": "object"},
                    "forecast_period": {"type": "string", "default": "2026-Q1"},
                    "store_ids": {"type": "array", "items": {"type": "string"}},
                    "product_ids": {"type": "array", "items": {"type": "string"}},
                },
                "required": [],
            },
        }


def create_inventory_agent(bedrock_client: Any = None) -> InventoryAgent:
    return InventoryAgent(bedrock_client=bedrock_client)

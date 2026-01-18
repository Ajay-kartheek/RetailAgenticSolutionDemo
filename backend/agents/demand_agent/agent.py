"""
Demand Intelligence Agent for SK Brands Retail.

This agent analyzes demand forecasts and provides insights about
expected demand patterns across stores and products.
"""

import json
from typing import Any, Callable
from datetime import datetime

from .prompts import DEMAND_AGENT_SYSTEM_PROMPT, DEMAND_AGENT_TASK_PROMPT
from .tools import (
    get_demand_forecasts,
    get_store_forecasts,
    get_product_forecasts,
    DEMAND_TOOLS,
)


class DemandAgent:
    """
    Demand Intelligence Agent that analyzes ML-generated demand forecasts.

    This agent retrieves and analyzes demand forecast data to provide
    insights about expected demand patterns, identify high-demand items,
    and flag low-confidence predictions.
    """

    def __init__(self, bedrock_client: Any = None):
        """
        Initialize the Demand Agent.

        Args:
            bedrock_client: Optional Bedrock client for LLM calls.
                           If not provided, will use the shared client.
        """
        self.name = "Demand Intelligence Agent"
        self.agent_id = "demand_agent"
        self.system_prompt = DEMAND_AGENT_SYSTEM_PROMPT

        if bedrock_client is None:
            from shared.bedrock import bedrock_client as default_client
            self.bedrock_client = default_client
        else:
            self.bedrock_client = bedrock_client

        # Register tools
        self.tools = {
            "get_demand_forecasts": get_demand_forecasts,
            "get_store_forecasts": get_store_forecasts,
            "get_product_forecasts": get_product_forecasts,
        }

        self.tool_definitions = DEMAND_TOOLS

    def get_tool_definitions_for_bedrock(self) -> list[dict]:
        """Get tool definitions formatted for Bedrock tool use."""
        return [
            {
                "toolSpec": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": {
                        "json": tool["parameters"]
                    }
                }
            }
            for tool in self.tool_definitions
        ]

    def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        """
        Execute a tool by name with given input.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
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
        task: str | None = None,
        forecast_period: str = "2026-Q1",
        store_ids: list[str] | None = None,
        product_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Run demand analysis using LLM reasoning with tool calling.

        Args:
            task: Optional natural language task description
            forecast_period: Forecast period to analyze
            store_ids: Optional list of specific stores to analyze
            product_ids: Optional list of specific products to analyze

        Returns:
            Demand analysis results
        """
        # Build the task prompt
        if not task:
            task = f"""Analyze demand forecasts for SK Brands retail stores for the period {forecast_period}.

Your objectives:
1. Get overall demand forecast data
2. Identify high-demand items that may need priority stocking
3. Flag low-confidence forecasts that need review
4. Provide actionable insights and recommendations

Use the available tools to retrieve and analyze the data."""

        # Prepare messages for Claude (Converse API expects content as list)
        messages = [{"role": "user", "content": [{"text": task}]}]

        # Track conversation and tool results
        tool_results_collected = []
        max_iterations = 5
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call Bedrock Claude with tool definitions
            response = self.bedrock_client.converse(
                modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                messages=messages,
                system=[{"text": self.system_prompt}],
                toolConfig={"tools": self.get_tool_definitions_for_bedrock()},
            )

            # Check stop reason
            stop_reason = response["stopReason"]

            # Add assistant response to messages
            assistant_message = response["output"]["message"]
            messages.append(assistant_message)

            if stop_reason == "tool_use":
                # Claude wants to use tools
                tool_use_blocks = [
                    block for block in assistant_message["content"]
                    if "toolUse" in block
                ]

                # Execute each tool
                tool_results = []
                for tool_block in tool_use_blocks:
                    tool_use = tool_block["toolUse"]
                    tool_name = tool_use["name"]
                    tool_input = tool_use["input"]
                    tool_use_id = tool_use["toolUseId"]

                    # Execute the tool
                    result = self.execute_tool(tool_name, tool_input)
                    tool_results_collected.append({
                        "tool": tool_name,
                        "input": tool_input,
                        "result": result
                    })

                    # Format result for Claude
                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tool_use_id,
                            "content": [{"json": result}]
                        }
                    })

                # Add tool results to messages
                messages.append({
                    "role": "user",
                    "content": tool_results
                })

            elif stop_reason == "end_turn":
                # Claude is done - extract final response
                final_text = ""
                for block in assistant_message["content"]:
                    if "text" in block:
                        final_text += block["text"]

                # Return structured results
                return {
                    "agent_id": self.agent_id,
                    "agent_name": self.name,
                    "timestamp": datetime.utcnow().isoformat(),
                    "forecast_period": forecast_period,
                    "llm_analysis": final_text,
                    "tool_calls": tool_results_collected,
                    "insights": self._extract_insights_from_llm_response(final_text),
                    "recommendations": self._extract_recommendations_from_llm_response(final_text),
                }

        # Max iterations reached
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "error": "Max iterations reached",
            "tool_calls": tool_results_collected,
        }

    def _extract_insights_from_llm_response(self, llm_text: str) -> list[str]:
        """Extract insights from Claude's text response."""
        insights = []
        lines = llm_text.split("\n")

        in_insights_section = False
        for line in lines:
            line = line.strip()
            if "insight" in line.lower() or "key finding" in line.lower():
                in_insights_section = True
                continue
            if in_insights_section and line.startswith("-"):
                insights.append(line[1:].strip())
            elif in_insights_section and (line.startswith("##") or line.startswith("**")):
                break

        # If no structured insights found, extract key sentences
        if not insights:
            sentences = llm_text.split(".")
            for sent in sentences[:5]:
                if len(sent.strip()) > 20:
                    insights.append(sent.strip())

        return insights[:5]  # Return top 5

    def _extract_recommendations_from_llm_response(self, llm_text: str) -> list[str]:
        """Extract recommendations from Claude's text response."""
        recommendations = []
        lines = llm_text.split("\n")

        in_rec_section = False
        for line in lines:
            line = line.strip()
            if "recommendation" in line.lower() or "action" in line.lower():
                in_rec_section = True
                continue
            if in_rec_section and line.startswith("-"):
                recommendations.append(line[1:].strip())
            elif in_rec_section and (line.startswith("##") or line.startswith("**")):
                break

        return recommendations[:5]  # Return top 5

    def as_tool(self) -> dict:
        """
        Return this agent as a tool definition for the orchestrator.

        Returns:
            Tool definition dict for use by orchestrator agent.
        """
        return {
            "name": "demand_agent",
            "description": (
                "Analyze demand forecasts for SK Brands stores. "
                "Returns demand predictions, high-demand items, low-confidence forecasts, "
                "and insights about expected demand patterns."
            ),
            "function": self.analyze,
            "parameters": {
                "type": "object",
                "properties": {
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
                },
                "required": [],
            },
        }


def create_demand_agent(bedrock_client: Any = None) -> DemandAgent:
    """
    Factory function to create a Demand Agent instance.

    Args:
        bedrock_client: Optional Bedrock client for LLM calls

    Returns:
        Configured DemandAgent instance
    """
    return DemandAgent(bedrock_client=bedrock_client)

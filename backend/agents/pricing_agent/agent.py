"""
Pricing & Promotion Agent for SK Brands Retail.
"""

from typing import Any
from datetime import datetime

from config.settings import settings
from shared.db import DynamoDBClient
from .prompts import PRICING_AGENT_SYSTEM_PROMPT
from .tools import create_pricing_recommendation, get_all_pricing_recommendations, PRICING_TOOLS


class PricingAgent:
    """Pricing Agent that generates pricing and promotion recommendations."""

    def __init__(self, bedrock_client: Any = None):
        self.name = "Pricing & Promotion Agent"
        self.agent_id = "pricing_agent"
        self.system_prompt = PRICING_AGENT_SYSTEM_PROMPT

        if bedrock_client is None:
            from shared.bedrock import bedrock_client as default_client
            self.bedrock_client = default_client
        else:
            self.bedrock_client = bedrock_client

        self.db_client = DynamoDBClient()

        self.tools = {
            "create_pricing_recommendation": create_pricing_recommendation,
            "get_all_pricing_recommendations": get_all_pricing_recommendations,
        }
        self.tool_definitions = PRICING_TOOLS

    def analyze(
        self,
        inventory_data: dict[str, Any] | None = None,
        trend_data: dict[str, Any] | None = None,
        forecast_period: str = "2026-Q1",
    ) -> dict[str, Any]:
        """Generate pricing recommendations."""
        results = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "forecast_period": forecast_period,
            "recommendations": [],
            "summary": {},
            "insights": [],
        }

        # Get active pricing decisions to avoid duplicates
        active_pricing_decisions = self.db_client.get_active_decisions(decision_type="pricing", days=30)
        products_with_active_changes = set()
        active_changes_context = []
        
        for decision in active_pricing_decisions:
            data = decision.get("data", {})
            product_id = data.get("product_id")
            if product_id:
                products_with_active_changes.add(product_id)
                active_changes_context.append({
                    "product_name": data.get("product_name"),
                    "product_id": product_id,
                    "current_price": data.get("current_price"),
                    "new_price": data.get("recommended_price"),
                    "valid_until": data.get("valid_until"),
                    "status": decision.get("status")
                })
        
        print(f"[Pricing Agent] Found {len(products_with_active_changes)} products with active price changes")

        # Get REAL pricing recommendations from DynamoDB (limited for performance)
        pricing_data = get_all_pricing_recommendations(
            inventory_data=inventory_data,
            trend_data=trend_data,
            forecast_period=forecast_period,
        )

        # Filter out products that already have active price changes
        all_recommendations = pricing_data.get("recommendations", [])
        recommendations = [
            rec for rec in all_recommendations 
            if rec.get("product_id") not in products_with_active_changes
        ][:50]  # Increased limit from 10 to 50
        
        skipped_count = len(all_recommendations) - len([r for r in all_recommendations if r.get("product_id") not in products_with_active_changes])
        if skipped_count > 0:
            print(f"[Pricing Agent] Skipped {skipped_count} products with existing active price changes")

        # Build task for LLM to analyze REAL pricing opportunities
        import json
        
        # Include context about existing active changes
        active_changes_text = ""
        if active_changes_context:
            active_changes_text = f"""
**IMPORTANT - Existing Active Price Changes (DO NOT recommend changes for these products):**
{json.dumps(active_changes_context[:5], indent=2)}

These products already have approved/executed price changes. Skip them in your analysis.
"""
        
        task = f"""Analyze pricing and promotion opportunities for SK Brands retail stores for period {forecast_period}.
{active_changes_text}
**New Pricing Recommendations (products without active changes):**
{json.dumps(recommendations, indent=2)}

**Context:**
- Trending products: {len(trend_data.get("trending_products", [])) if trend_data else 0}
- Slow-moving products: {len(trend_data.get("slow_moving_products", [])) if trend_data else 0}
- Overstocked items: {len(inventory_data.get("overstocked_items", [])) if inventory_data else 0}

Provide:
1. Strategic pricing insights (which items to discount, which can be increased)
2. Promotion recommendations for slow-moving and overstocked items
3. Revenue optimization strategies
4. Identify high-impact pricing decisions that need HITL approval
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
            results["recommendations"] = recommendations
            results["summary"] = pricing_data.get("summary", {})
            results["insights"] = self._extract_insights_from_llm(llm_response)

            # Save decisions to database for HITL
            self._save_decisions(recommendations)

        except Exception as e:
            results["error"] = str(e)
            results["recommendations"] = recommendations
            results["insights"] = [f"Error during LLM analysis: {str(e)}"]

        return results

    def _save_decisions(self, recommendations: list[dict]):
        """Save recommendations as decisions in DynamoDB."""
        for rec in recommendations:
            try:
                # Generate unique decision ID if missing
                decision_id = rec.get("id") or f"PRICE_{datetime.utcnow().strftime('%Y%m%d')}_{rec.get('product_id')}"

                decision_record = {
                    "decision_id": decision_id,
                    "status": "pending",  # Pricing changes usually require approval
                    "timestamp": datetime.utcnow().isoformat(),
                    "decision_type": "pricing_" + (rec.get("recommendation_type") or "change"),
                    "agent_id": self.agent_id,
                    "title": f"Adjust Price for {rec.get('product_name')}",
                    "description": rec.get("reasoning", "Price adjustment recommended."),
                    "priority": "normal",
                    "cost": "0", # Price change itself has 0 immediate cost, impacts revenue
                    "impact": f"Exp. Revenue Impact: {rec.get('expected_revenue_impact_weekly', 'Unknown')}",
                    "data": rec
                }
                self.db_client.put_item(settings.decisions_table, decision_record)
            except Exception as e:
                print(f"Error saving pricing decision: {e}")

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

    def _generate_insights(self, data: dict) -> list[str]:
        insights = []
        summary = data.get("summary", {})

        discounts = summary.get("discounts", 0)
        increases = summary.get("increases", 0)
        impact = summary.get("total_expected_weekly_impact", 0)

        if discounts:
            insights.append(f"{discounts} products recommended for price reduction/promotion")
        if increases:
            insights.append(f"{increases} products can support price increases")
        if impact:
            insights.append(f"Expected weekly revenue impact: ₹{impact:,.0f}")

        return insights

    def apply_price_change(self, decision_data: dict) -> dict:
        """
        Execute an approved pricing decision.
        
        This updates the product price in the database and logs the action.
        
        Args:
            decision_data: The pricing recommendation data from the decision
            
        Returns:
            Execution result with activity log
        """
        try:
            product_id = decision_data.get("product_id")
            product_name = decision_data.get("product_name", product_id)
            current_price = decision_data.get("current_price", 0)
            # Use recommended_price OR suggested_price (fallback)
            new_price = decision_data.get("recommended_price") or decision_data.get("suggested_price", current_price)
            recommendation_type = decision_data.get("recommendation_type", "change")
            
            # Calculate the change
            price_change = new_price - current_price
            change_percent = (price_change / current_price * 100) if current_price else 0
            
            # Actually update the price in the products table
            try:
                from config.aws import get_dynamodb_resource
                from decimal import Decimal
                dynamodb = get_dynamodb_resource()
                products_table = dynamodb.Table(settings.products_table)
                
                products_table.update_item(
                    Key={"product_id": product_id},
                    UpdateExpression="SET price = :new_price",
                    ExpressionAttributeValues={":new_price": Decimal(str(new_price))}
                )
                print(f"[Pricing Agent] Updated price for {product_id}: ₹{current_price} → ₹{new_price}")
            except Exception as e:
                print(f"[Pricing Agent] Warning: Could not update product price: {e}")
            
            activity_log = []
            
            # Log the action
            activity_log.append({
                "action": "price_update",
                "product_id": product_id,
                "product_name": product_name,
                "old_price": current_price,
                "new_price": new_price,
                "change_percent": round(change_percent, 1),
                "type": recommendation_type,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Store activity in agent_activity table
            self._log_activity(
                action_type="price_change",
                description=f"Updated price for {product_name}: ₹{current_price} → ₹{new_price} ({change_percent:+.1f}%)",
                details={
                    "product_id": product_id,
                    "old_price": current_price,
                    "new_price": new_price,
                    "recommendation_type": recommendation_type
                }
            )
            
            return {
                "status": "executed",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Price updated for {product_name}: ₹{current_price} → ₹{new_price}",
                "activity_log": activity_log,
                "details": {
                    "product_id": product_id,
                    "product_name": product_name,
                    "old_price": current_price,
                    "new_price": new_price,
                    "change_percent": round(change_percent, 1)
                }
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _log_activity(self, action_type: str, description: str, details: dict = None):
        """Log agent activity to the database."""
        try:
            import uuid
            activity_record = {
                "activity_id": f"ACT_{uuid.uuid4().hex[:8].upper()}",
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "action_type": action_type,
                "description": description,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            self.db_client.put_item(settings.agent_activity_table, activity_record)
        except Exception as e:
            print(f"Error logging activity: {e}")

    def as_tool(self) -> dict:
        return {
            "name": "pricing_agent",
            "description": "Generate pricing and promotion recommendations based on inventory and trend data",
            "function": self.analyze,
            "parameters": {
                "type": "object",
                "properties": {
                    "inventory_data": {"type": "object"},
                    "trend_data": {"type": "object"},
                    "forecast_period": {"type": "string", "default": "2026-Q1"},
                },
                "required": [],
            },
        }


def create_pricing_agent(bedrock_client: Any = None) -> PricingAgent:
    return PricingAgent(bedrock_client=bedrock_client)

"""
Orchestrator Agent for SK Brands Retail Intelligence Platform.

This agent coordinates all specialist agents and synthesizes their outputs
into actionable intelligence with HITL decision points.
"""

from typing import Any, Callable, Generator
from datetime import datetime
import uuid
import re
import json

from config.settings import settings
from shared.db import DynamoDBClient
from .prompts import ORCHESTRATOR_SYSTEM_PROMPT, ORCHESTRATOR_TASK_PROMPT


class OrchestratorAgent:
    """
    Orchestrator Agent that coordinates all specialist agents.

    Executes agents in sequence, passing data between them, and
    synthesizes findings into a unified report.
    """

    def __init__(self, bedrock_client: Any = None):
        self.name = "SK Brands Orchestrator"
        self.agent_id = "orchestrator"
        self.system_prompt = ORCHESTRATOR_SYSTEM_PROMPT

        if bedrock_client is None:
            from shared.bedrock import bedrock_client as default_client
            self.bedrock_client = default_client
        else:
            self.bedrock_client = bedrock_client

        # Initialize specialist agents lazily
        self._demand_agent = None
        self._trend_agent = None
        self._inventory_agent = None
        self._replenishment_agent = None
        self._pricing_agent = None
        self._campaign_agent = None

    @property
    def demand_agent(self):
        if self._demand_agent is None:
            from agents.demand_agent.agent import create_demand_agent
            self._demand_agent = create_demand_agent(self.bedrock_client)
        return self._demand_agent

    @property
    def trend_agent(self):
        if self._trend_agent is None:
            from agents.trend_agent.agent import create_trend_agent
            self._trend_agent = create_trend_agent(self.bedrock_client)
        return self._trend_agent

    @property
    def inventory_agent(self):
        if self._inventory_agent is None:
            from agents.inventory_agent.agent import create_inventory_agent
            self._inventory_agent = create_inventory_agent(self.bedrock_client)
        return self._inventory_agent

    @property
    def replenishment_agent(self):
        if self._replenishment_agent is None:
            from agents.replenishment_agent.agent import create_replenishment_agent
            self._replenishment_agent = create_replenishment_agent(self.bedrock_client)
        return self._replenishment_agent

    @property
    def pricing_agent(self):
        if self._pricing_agent is None:
            from agents.pricing_agent.agent import create_pricing_agent
            self._pricing_agent = create_pricing_agent(self.bedrock_client)
        return self._pricing_agent

    @property
    def campaign_agent(self):
        if self._campaign_agent is None:
            from agents.campaign_agent.agent import create_campaign_agent
            self._campaign_agent = create_campaign_agent(self.bedrock_client)
        return self._campaign_agent

    def get_agent_tools_for_bedrock(self) -> list[dict]:
        """Get specialist agents as tools for the orchestrator LLM."""
        return [
            {
                "toolSpec": {
                    "name": "demand_agent",
                    "description": "Analyze demand forecasts for stores and products. Returns high-demand items, forecasts, and demand insights. Call this FIRST to get baseline demand data.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "forecast_period": {"type": "string", "description": "Period like '2026-Q1'"},
                                "store_ids": {"type": "array", "items": {"type": "string"}},
                                "product_ids": {"type": "array", "items": {"type": "string"}},
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "trend_agent",
                    "description": "Analyze sales trends by comparing actual sales vs demand forecasts. Identifies trending and slow-moving products. Call AFTER demand_agent.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "forecast_period": {"type": "string"},
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "inventory_agent",
                    "description": "Analyze inventory status based on trend data. Identifies understocked, overstocked, and critical items. Call AFTER trend_agent.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "forecast_period": {"type": "string"},
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "replenishment_agent",
                    "description": "Create replenishment plans for understocked items. Analyzes inter-store transfers and manufacturer orders. Call AFTER inventory_agent.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "forecast_period": {"type": "string"},
                            }
                        }
                    }
                }
            },
            {
                "toolSpec": {
                    "name": "pricing_agent",
                    "description": "Generate pricing and promotion recommendations based on inventory status and trends. Call AFTER inventory_agent.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "forecast_period": {"type": "string"},
                            }
                        }
                    }
                }
            },
        ]

    def run(
        self,
        forecast_period: str = "2026-Q1",
        store_ids: list[str] | None = None,
        product_ids: list[str] | None = None,
        include_campaigns: bool = False,
        on_progress: Callable[[dict], None] | None = None,
    ) -> dict[str, Any]:
        """
        Run the full orchestration workflow.

        Args:
            forecast_period: Forecast period to analyze
            store_ids: Optional specific stores
            product_ids: Optional specific products
            include_campaigns: Whether to generate campaign suggestions
            on_progress: Callback for progress updates

        Returns:
            Complete orchestration results
        """
        run_id = f"RUN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6].upper()}"

        results = {
            "run_id": run_id,
            "orchestrator_id": self.agent_id,
            "started_at": datetime.utcnow().isoformat(),
            "forecast_period": forecast_period,
            "agents_executed": [],
            "agent_results": {},
            "tool_calls": [],
            "status": "running",
        }

        def emit_progress(agent_name: str, status: str, message: str, data: Any = None, thinking: str = None):
            if on_progress:
                progress_data = {
                    "run_id": run_id,
                    "agent_name": agent_name,
                    "status": status,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                if data:
                    progress_data["data"] = data
                if thinking:
                    progress_data["thinking"] = thinking
                on_progress(progress_data)

        # Build task for Orchestrator LLM
        task = f"""Coordinate SK Brands retail intelligence analysis for period {forecast_period}.

Your goal: Run specialist agents to analyze demand, trends, inventory, replenishment needs, pricing, and campaigns.

**Process:**
1. Start with demand_agent to get forecast data
2. Use trend_agent with demand data to analyze sales velocity
3. Use inventory_agent with trend data to identify stock issues
4. For each agent, extract and synthesize key insights

**Output:** Provide executive summary with prioritized actions.
"""

        # Prepare messages for Claude Orchestrator
        messages = [{"role": "user", "content": [{"text": task}]}]

        max_iterations = 10
        iteration = 0

        try:
            while iteration < max_iterations:
                iteration += 1

                emit_progress("Orchestrator", "running", f"Orchestrator Claude is coordinating agents (iteration {iteration})...",
                             thinking="Orchestrator LLM is deciding which agent to call next based on current context")

                # Call Bedrock Claude with agent tools
                response = self.bedrock_client.converse(
                    modelId="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
                    messages=messages,
                    system=[{"text": self.system_prompt}],
                    toolConfig={"tools": self.get_agent_tools_for_bedrock()},
                )

                stop_reason = response["stopReason"]
                assistant_message = response["output"]["message"]
                messages.append(assistant_message)

                if stop_reason == "tool_use":
                    # Claude wants to call an agent
                    tool_use_blocks = [b for b in assistant_message["content"] if "toolUse" in b]

                    tool_results = []
                    for tool_block in tool_use_blocks:
                        tool_use = tool_block["toolUse"]
                        agent_name = tool_use["name"]
                        tool_input = tool_use["input"]
                        tool_use_id = tool_use["toolUseId"]

                        emit_progress(agent_name, "running", f"Orchestrator calling {agent_name}...",
                                     thinking=f"Orchestrator Claude decided to call {agent_name} with params: {tool_input}")

                        # Execute the agent
                        agent_result = self._execute_agent(agent_name, tool_input, emit_progress)

                        results["tool_calls"].append({
                            "agent": agent_name,
                            "input": tool_input,
                            "result": agent_result
                        })
                        results["agents_executed"].append(agent_name)
                        results["agent_results"][agent_name] = agent_result

                        # Format result for Claude
                        tool_results.append({
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"json": agent_result}]
                            }
                        })

                    # Add tool results back to messages
                    messages.append({"role": "user", "content": tool_results})

                elif stop_reason == "end_turn":
                    # Claude is done coordinating
                    final_text = ""
                    for block in assistant_message["content"]:
                        if "text" in block:
                            final_text += block["text"]

                    results["executive_summary"] = final_text
                    results["status"] = "completed"
                    results["completed_at"] = datetime.utcnow().isoformat()

                    # Generate and store structured summaries for Agent Insights
                    emit_progress("Orchestrator", "running", "Synthesizing structured agent reports...",
                                 thinking="Generating final insights and recommendations for dashboard")

                    try:
                        structured_results = self._generate_structured_summaries(results)
                        self._store_agent_results(run_id, structured_results)
                        # Store detailed insights for table display
                        self._store_detailed_insights(run_id, forecast_period)
                        # Add to final results
                        results["structured_agent_outputs"] = structured_results
                    except Exception as e:
                        print(f"Error generating/storing agent summaries: {e}")
                    
                    emit_progress("Orchestrator", "completed", "Orchestration complete",
                                 thinking=final_text[:200])
                        
                    break

            if iteration >= max_iterations:
                results["status"] = "max_iterations_reached"

        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            emit_progress("Orchestrator", "failed", f"Error: {str(e)}")

        return results

    def execute_decision(self, decision_id: str, decision_type: str, data: dict) -> dict:
        """
        Execute an approved human decision via the appropriate specialist agent.
        
        Args:
            decision_id: The ID of the decision
            decision_type: Type string (e.g. 'replenishment_transfer', 'pricing_discount')
            data: The original decision payload
            
        Returns:
            Execution result details
        """
        try:
            print(f"[Orchestrator] Executing decision {decision_id} of type {decision_type}")
            
            if "replenishment" in decision_type:
                # Use property to lazy load and execute
                print(f"[Orchestrator] Delegating to Replenishment Agent")
                result = self.replenishment_agent.process_transfer(data)
                return result
            
            elif "pricing" in decision_type:
                # Execute pricing change via pricing agent
                print(f"[Orchestrator] Delegating to Pricing Agent")
                result = self.pricing_agent.apply_price_change(data)
                return result
            
            elif "promotion" in decision_type or "campaign" in decision_type:
                # For promotions/campaigns, log the activation
                print(f"[Orchestrator] Delegating to Campaign Agent")
                # Campaign agent would handle this
                return {
                    "status": "executed",
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Promotion activated for {data.get('product_name', 'products')}"
                }
            
            else:
                print(f"[Orchestrator] No specific handler for {decision_type}, marking as executed")
                return {
                    "status": "executed", 
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Decision {decision_id} executed (generic handler)"
                }
            
        except Exception as e:
            print(f"[Orchestrator] Error executing decision {decision_id}: {e}")
            return {"status": "failed", "error": str(e)}

    def _execute_agent(self, agent_name: str, tool_input: dict, emit_progress: Callable) -> dict[str, Any]:
        """Execute a specialist agent by name, using stored context from previous agents."""
        try:
            forecast_period = tool_input.get("forecast_period", "2026-Q1")
            
            if agent_name == "demand_agent":
                emit_progress("demand_agent", "running", "Analyzing demand forecasts...",
                             thinking="Retrieving ML demand predictions from DynamoDB")
                result = self.demand_agent.analyze(
                    forecast_period=forecast_period,
                    store_ids=tool_input.get("store_ids"),
                    product_ids=tool_input.get("product_ids"),
                )
                # Store demand data for other agents
                self._demand_data = result
                thinking = result.get("llm_analysis", "")[:300] if result.get("llm_analysis") else "Demand analysis complete"
                
                # Extract forecast count from tool calls (data is nested in tool_calls)
                forecast_count = 0
                total_demand = 0
                for tc in result.get("tool_calls", []):
                    if tc.get("tool") == "get_demand_forecasts":
                        tool_result = tc.get("result", {})
                        forecast_count = len(tool_result.get("forecasts", []))
                        summary = tool_result.get("summary", {})
                        total_demand = summary.get("total_forecasted_demand", 0)
                        break
                
                message = f"Analyzed {forecast_count} forecasts, {total_demand:,} units total demand"
                emit_progress("demand_agent", "completed", message, thinking=thinking)
                return result

            elif agent_name == "trend_agent":
                emit_progress("trend_agent", "running", "Analyzing sales trends...",
                             thinking="Comparing actual sales vs forecasts to identify trending products")
                # Use stored demand data
                result = self.trend_agent.analyze(
                    demand_data=getattr(self, '_demand_data', None),
                    forecast_period=forecast_period,
                )
                # Store trend data for other agents
                self._trend_data = result
                thinking = result.get("llm_analysis", "")[:300] if result.get("llm_analysis") else "Trend analysis complete"
                summary = result.get("summary", {})
                emit_progress("trend_agent", "completed", 
                             f"{summary.get('total_in_trend', 0)} trending, {summary.get('total_slow_moving', 0)} slow",
                             thinking=thinking)
                return result

            elif agent_name == "inventory_agent":
                emit_progress("inventory_agent", "running", "Analyzing inventory levels...",
                             thinking="Classifying stock as understocked, in-stock, or overstocked")
                # Use stored trend data
                result = self.inventory_agent.analyze(
                    trend_data=getattr(self, '_trend_data', None),
                    forecast_period=forecast_period,
                )
                # Store inventory data for other agents
                self._inventory_data = result
                thinking = result.get("llm_analysis", "")[:300] if result.get("llm_analysis") else "Inventory analysis complete"
                summary = result.get("summary", {})
                emit_progress("inventory_agent", "completed",
                             f"{summary.get('critical_count', 0)} critical, {summary.get('understocked_count', 0)} understocked",
                             thinking=thinking)
                return result

            elif agent_name == "replenishment_agent":
                emit_progress("replenishment_agent", "running", "Creating replenishment plans...",
                             thinking="Evaluating inter-store transfers vs manufacturer orders")
                # Use stored inventory data (replenishment agent doesn't need trend_data)
                result = self.replenishment_agent.analyze(
                    inventory_data=getattr(self, '_inventory_data', None),
                    forecast_period=forecast_period,
                )
                thinking = result.get("llm_analysis", "")[:300] if result.get("llm_analysis") else "Replenishment plans created"
                plans = result.get("plans", [])
                emit_progress("replenishment_agent", "completed",
                             f"Created {len(plans)} replenishment plans",
                             thinking=thinking)
                return result

            elif agent_name == "pricing_agent":
                emit_progress("pricing_agent", "running", "Generating pricing recommendations...",
                             thinking="Analyzing inventory and trends to suggest optimal pricing")
                # Use stored data
                result = self.pricing_agent.analyze(
                    inventory_data=getattr(self, '_inventory_data', None),
                    trend_data=getattr(self, '_trend_data', None),
                    forecast_period=forecast_period,
                )
                thinking = result.get("llm_analysis", "")[:300] if result.get("llm_analysis") else "Pricing recommendations ready"
                recs = result.get("recommendations", [])
                emit_progress("pricing_agent", "completed",
                             f"Generated {len(recs)} pricing recommendations",
                             thinking=thinking)
                return result

            else:
                return {"error": f"Unknown agent: {agent_name}"}

        except Exception as e:
            emit_progress(agent_name, "error", f"Agent error: {str(e)}")
            return {"error": str(e)}

    def run_streaming(
        self,
        forecast_period: str = "2026-Q1",
        store_ids: list[str] | None = None,
        product_ids: list[str] | None = None,
        include_campaigns: bool = False,
    ) -> Generator[dict[str, Any], None, None]:
        """
        Run orchestration with streaming updates.

        Yields progress updates as each agent completes.
        """
        updates = []

        def collect_progress(update: dict):
            updates.append(update)

        # Run with progress collection
        final_results = self.run(
            forecast_period=forecast_period,
            store_ids=store_ids,
            product_ids=product_ids,
            include_campaigns=include_campaigns,
            on_progress=collect_progress,
        )

        # Yield collected updates
        for update in updates:
            yield update

        # Yield final results
        yield {
            "type": "final_results",
            "results": final_results,
        }

    def _extract_key_findings(self, results: dict) -> list[dict]:
        """Extract key findings from all agent results."""
        findings = []

        # From demand
        demand = results.get("agent_results", {}).get("demand", {})
        for insight in demand.get("insights", []):
            findings.append({"agent": "demand", "finding": insight, "priority": "medium"})

        # From trend
        trend = results.get("agent_results", {}).get("trend", {})
        for insight in trend.get("insights", []):
            priority = "high" if "URGENT" in insight or "critical" in insight.lower() else "medium"
            findings.append({"agent": "trend", "finding": insight, "priority": priority})

        # From inventory
        inventory = results.get("agent_results", {}).get("inventory", {})
        for insight in inventory.get("insights", []):
            priority = "high" if "CRITICAL" in insight else "medium"
            findings.append({"agent": "inventory", "finding": insight, "priority": priority})

        # From replenishment
        replenishment = results.get("agent_results", {}).get("replenishment", {})
        for insight in replenishment.get("insights", []):
            priority = "high" if "URGENT" in insight else "medium"
            findings.append({"agent": "replenishment", "finding": insight, "priority": priority})

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        findings.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

        return findings

    def _prioritize_actions(self, results: dict) -> list[dict]:
        """Create prioritized action list from all agent recommendations."""
        actions = []

        # Critical replenishment
        replenishment = results.get("agent_results", {}).get("replenishment", {})
        for plan in replenishment.get("plans", []):
            if plan.get("urgency") == "critical":
                actions.append({
                    "priority": 1,
                    "type": "replenishment",
                    "action": f"Replenish {plan.get('product_name')} at {plan.get('target_store_id')}",
                    "cost": plan.get("total_cost"),
                    "details": plan,
                })

        # High-impact pricing
        pricing = results.get("agent_results", {}).get("pricing", {})
        for rec in pricing.get("recommendations", [])[:5]:  # Top 5
            actions.append({
                "priority": 2,
                "type": "pricing",
                "action": f"Adjust pricing for {rec.get('product_name')} ({rec.get('recommendation_type')})",
                "expected_impact": rec.get("expected_revenue_impact_weekly"),
                "details": rec,
            })

        # Sort by priority
        actions.sort(key=lambda x: x.get("priority", 99))

        return actions

    def _generate_executive_summary(self, results: dict) -> str:
        """Generate executive summary from all results."""
        parts = []

        # Overall status
        agents_run = len(results.get("agents_executed", []))
        parts.append(f"Completed analysis across {agents_run} specialist agents.")

        # Key metrics
        inventory = results.get("agent_results", {}).get("inventory", {})
        summary = inventory.get("summary", {})
        if summary:
            critical = summary.get("critical_count", 0)
            if critical > 0:
                parts.append(f"ALERT: {critical} critical inventory situations require immediate attention.")

        # Trend highlights
        trend = results.get("agent_results", {}).get("trend", {})
        trend_summary = trend.get("summary", {})
        if trend_summary:
            in_trend = trend_summary.get("total_in_trend", 0)
            slow = trend_summary.get("total_slow_moving", 0) + trend_summary.get("total_no_trend", 0)
            if in_trend:
                parts.append(f"{in_trend} products are trending above expectations.")
            if slow:
                parts.append(f"{slow} products are underperforming and may need attention.")

        # Actions pending
        decisions = len(results.get("decisions_requiring_approval", []))
        if decisions:
            parts.append(f"{decisions} decisions are awaiting approval in the decision queue.")

        return " ".join(parts)

    def _generate_structured_summaries(self, results: dict) -> dict:
        """
        Ask Claude to generate clean, structured summaries for each agent 
        based on their raw outputs.
        """

        try:
            with open("debug_log.txt", "a") as f:
                f.write(f"{datetime.utcnow()}: Generating structured summaries. Keys in results: {list(results.keys())}\n")
                if "agent_results" in results:
                    f.write(f"{datetime.utcnow()}: Agent results keys: {list(results['agent_results'].keys())}\n")
                else:
                    f.write(f"{datetime.utcnow()}: No agent_results found!\n")

            bedrock_client = self.bedrock_client
            agent_results = results.get("agent_results", {})
            
            if not agent_results:
                return {}

            # Prepare context from agent results
            context = "Here are the detailed outputs from the specialist agents:\n\n"
            for agent_name, agent_data in agent_results.items():
                context += f"--- {agent_name.upper()} ---\n"
                context += json.dumps(agent_data, indent=2) + "\n\n"

            prompt = (
                "You are an expert retail analyst. \n"
                "Review the following agent outputs and generate a structured summary for EACH agent.\n\n"
                f"Context:\n{context}\n\n"
                "Required Output Format (JSON):\n"
                "{\n"
                '    "demand_agent": {\n'
                '        "summary": "Brief executive summary...",\n'
                '        "insights": ["Insight 1", "..."],\n'
                '        "recommendations": ["Rec 1", "..."],\n'
                '        "metrics": { "key": "value" }\n'
                "    },\n"
                "    ... for all agents present.\n"
                "}\n\n"
                "IMPORTANT: Return ONLY the JSON object. No preamble.\n"
                "Ensure keys match the agent names exactly as provided in the context header (lowercase, underscores)."
            )

            # Call Bedrock
            # Note: optimization - reduced max_tokens to prevent timeouts
            # Call Bedrock using wrapper
            content = bedrock_client.invoke_claude(
                prompt=prompt,
                temperature=0.1
            )
            
            with open("debug_log.txt", "a") as f:
                f.write(f"{datetime.utcnow()}: Raw LLM Response length: {len(content)}\n")
                f.write(f"{datetime.utcnow()}: Raw LLM Response sample: {content[:200]}\n")
            
            # Extract JSON
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                with open("debug_log.txt", "a") as f:
                    f.write(f"{datetime.utcnow()}: No JSON found in response\n")
                return {}
                
        except Exception as e:
            print(f"Error extracting structured data: {e}")
            with open("debug_log.txt", "a") as f:
                f.write(f"{datetime.utcnow()}: Exception in generate_structured_summaries: {e}\n")
            return {}

    def _store_agent_results(self, run_id: str, structured_results: dict):
        # Store structured results in DynamoDB.
        if not structured_results:
            with open("debug_log.txt", "a") as f:
                f.write(f"{datetime.now()}: Structured results empty\n")
            return
            
        db = DynamoDBClient()
        timestamp = datetime.utcnow().isoformat()
        
        # Canonical map for agent IDs
        allowed_map = {
            "orchestrator": "Orchestrator",
            "demand": "demand_agent",
            "trend": "trend_agent",
            "inventory": "inventory_agent",
            "replenishment": "replenishment_agent",
            "pricing": "pricing_agent",
            "campaign": "campaign_agent"
        }
        
        # Batch write items
        for raw_agent_id, data in structured_results.items():
            # Normalize agent_id
            key = raw_agent_id.lower().replace("_agent", "").replace(" agent", "").strip()
            agent_id = allowed_map.get(key, raw_agent_id)
            
            item = {
                "run_id": run_id,
                "agent_id": agent_id, 
                "timestamp": timestamp,
                "summary": data.get("summary", ""),
                "insights": data.get("insights", []),
                "recommendations": data.get("recommendations", []),
                "metrics": data.get("metrics", {})
            }
            # We treat 'agent_runs_table' as the target
            try:
                db.put_item(settings.agent_runs_table, item)
                with open("debug_log.txt", "a") as f:
                    f.write(f"{datetime.now()}: Stored {agent_id} for run {run_id}\n")
            except Exception as e:
                with open("debug_log.txt", "a") as f:
                    f.write(f"{datetime.now()}: Error storing item {agent_id}: {e}\n")

    def _store_detailed_insights(self, run_id: str, forecast_period: str):
        """
        Compute and store detailed table insights from each agent.
        This data will be read by the /agents/*/insights endpoints.
        """
        from datetime import datetime
        import requests
        
        db = DynamoDBClient()
        timestamp = datetime.utcnow().isoformat()
        
        # Base URL for internal API calls
        base_url = "http://localhost:8000"
        
        agent_endpoints = {
            "demand": f"{base_url}/agents/demand/insights?period={forecast_period}",
            "trend": f"{base_url}/agents/trend/insights?period={forecast_period}",
            "inventory": f"{base_url}/agents/inventory/insights?period={forecast_period}",
            "replenishment": f"{base_url}/agents/replenishment/insights?period={forecast_period}",
            "pricing": f"{base_url}/agents/pricing/insights?period={forecast_period}",
        }
        
        for agent_type, endpoint in agent_endpoints.items():
            try:
                # Call the insights endpoint to get computed data
                response = requests.get(endpoint, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store in agent_insights table
                    item = {
                        "agent_type": agent_type,
                        "run_id": run_id,
                        "timestamp": timestamp,
                        "insights": data.get("insights", []),
                        "summary": data.get("summary", {}),
                        "forecast_period": forecast_period,
                    }
                    db.put_item(settings.agent_insights_table, item)
                    
                    with open("debug_log.txt", "a") as f:
                        f.write(f"{datetime.now()}: Stored {len(item.get('insights', []))} insights for {agent_type}\n")
                else:
                    with open("debug_log.txt", "a") as f:
                        f.write(f"{datetime.now()}: Failed to fetch {agent_type} insights: {response.status_code}\n")
                        
            except Exception as e:
                with open("debug_log.txt", "a") as f:
                    f.write(f"{datetime.now()}: Error storing detailed insights for {agent_type}: {e}\n")


def create_orchestrator_agent(bedrock_client: Any = None) -> OrchestratorAgent:
    return OrchestratorAgent(bedrock_client=bedrock_client)

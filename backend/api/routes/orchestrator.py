"""
Orchestrator Routes - Main Agent Execution
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import asyncio
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from agents.orchestrator import OrchestratorAgent

router = APIRouter()
logger = logging.getLogger(__name__)


class OrchestratorRequest(BaseModel):
    """Request model for orchestrator run."""
    forecast_period: str = "2026-Q1"
    store_ids: Optional[List[str]] = None
    product_ids: Optional[List[str]] = None
    include_campaigns: bool = True


class OrchestratorStatus:
    """Track orchestrator execution status."""
    def __init__(self):
        self.runs = {}

    def start_run(self, run_id: str):
        self.runs[run_id] = {
            "status": "running",
            "progress": [],
            "result": None,
            "error": None
        }

    def add_progress(self, run_id: str, message: str):
        if run_id in self.runs:
            self.runs[run_id]["progress"].append(message)

    def complete_run(self, run_id: str, result: dict):
        if run_id in self.runs:
            self.runs[run_id]["status"] = "completed"
            self.runs[run_id]["result"] = result

    def fail_run(self, run_id: str, error: str):
        if run_id in self.runs:
            self.runs[run_id]["status"] = "failed"
            self.runs[run_id]["error"] = error

    def get_run(self, run_id: str):
        return self.runs.get(run_id)


status_tracker = OrchestratorStatus()


@router.post("/run")
async def run_orchestrator(request: OrchestratorRequest):
    """
    Run the full orchestrator agent flow.

    This executes all agents in sequence:
    1. Demand Agent - Get demand forecasts
    2. Trend Agent - Analyze sales trends
    3. Inventory Agent - Assess stock levels
    4. Replenishment Agent - Create replenishment plans
    5. Pricing Agent - Generate pricing recommendations
    6. Campaign Agent - Create marketing campaigns (optional)
    """
    import uuid
    run_id = str(uuid.uuid4())

    logger.info(f"Starting orchestrator run {run_id}")

    try:
        orchestrator = OrchestratorAgent()

        progress_messages = []

        def on_progress(message: str):
            progress_messages.append(message)
            logger.info(f"[{run_id}] {message}")

        result = orchestrator.run(
            forecast_period=request.forecast_period,
            store_ids=request.store_ids,
            product_ids=request.product_ids,
            include_campaigns=request.include_campaigns,
            on_progress=on_progress
        )

        return {
            "run_id": run_id,
            "status": "completed",
            "progress": progress_messages,
            "result": result
        }

    except Exception as e:
        logger.error(f"Orchestrator run {run_id} failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run/stream")
async def run_orchestrator_stream(request: OrchestratorRequest):
    """
    Run orchestrator with Server-Sent Events for real-time progress updates.
    """
    import uuid
    run_id = str(uuid.uuid4())

    async def generate():
        try:
            orchestrator = OrchestratorAgent()

            # Queue to hold progress messages
            progress_queue = asyncio.Queue()
            result_holder = {"result": None, "error": None}

            def on_progress(progress_data: dict):
                # Put progress in queue (will be processed by async loop)
                try:
                    # Pass ALL fields from progress_data to frontend
                    event_data = {
                        "type": "progress",
                        "agent_name": progress_data.get("agent_name", "Orchestrator"),
                        "status": progress_data.get("status", "running"),
                        "message": progress_data.get("message", "Processing..."),
                    }
                    if progress_data.get("thinking"):
                        event_data["thinking"] = progress_data["thinking"]
                    if progress_data.get("data"):
                        event_data["data"] = progress_data["data"]

                    progress_queue.put_nowait(event_data)
                except:
                    pass

            # Run orchestrator in thread pool
            def run_sync():
                try:
                    result = orchestrator.run(
                        forecast_period=request.forecast_period,
                        store_ids=request.store_ids,
                        product_ids=request.product_ids,
                        include_campaigns=request.include_campaigns,
                        on_progress=on_progress
                    )
                    result_holder["result"] = result
                except Exception as e:
                    result_holder["error"] = str(e)
                finally:
                    try:
                        progress_queue.put_nowait({"type": "done"})
                    except:
                        pass

            # Start orchestrator in background
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(None, run_sync)

            # Yield progress events
            yield f"data: {json.dumps({'type': 'start', 'run_id': run_id})}\n\n"

            while True:
                try:
                    item = await asyncio.wait_for(progress_queue.get(), timeout=0.5)

                    if item["type"] == "done":
                        break

                    yield f"data: {json.dumps(item)}\n\n"

                except asyncio.TimeoutError:
                    # Send heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"

            # Wait for task to complete
            await task

            # Send final result
            if result_holder["error"]:
                yield f"data: {json.dumps({'type': 'error', 'error': result_holder['error']})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'complete', 'result': result_holder['result']})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.post("/run/background")
async def run_orchestrator_background(
    request: OrchestratorRequest,
    background_tasks: BackgroundTasks
):
    """
    Start orchestrator run in background and return immediately.
    Use GET /orchestrator/status/{run_id} to check progress.
    """
    import uuid
    run_id = str(uuid.uuid4())

    status_tracker.start_run(run_id)

    def run_in_background():
        try:
            orchestrator = OrchestratorAgent()

            def on_progress(message: str):
                status_tracker.add_progress(run_id, message)

            result = orchestrator.run(
                forecast_period=request.forecast_period,
                store_ids=request.store_ids,
                product_ids=request.product_ids,
                include_campaigns=request.include_campaigns,
                on_progress=on_progress
            )

            status_tracker.complete_run(run_id, result)

        except Exception as e:
            logger.error(f"Background run {run_id} failed: {e}", exc_info=True)
            status_tracker.fail_run(run_id, str(e))

    background_tasks.add_task(run_in_background)

    return {
        "run_id": run_id,
        "status": "started",
        "message": "Orchestrator run started in background. Check status at /orchestrator/status/{run_id}"
    }


@router.get("/status/{run_id}")
async def get_orchestrator_status(run_id: str):
    """Get status of a background orchestrator run."""
    run_status = status_tracker.get_run(run_id)

    if not run_status:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")

    return {
        "run_id": run_id,
        **run_status
    }


@router.get("/agents")
async def list_agents():
    """List all available agents and their descriptions."""
    return {
        "agents": [
            {
                "name": "Demand Agent",
                "description": "Retrieves and analyzes demand forecasts from ML models",
                "inputs": ["forecast_period", "store_ids", "product_ids"],
                "outputs": ["demand_forecasts"]
            },
            {
                "name": "Trend Agent",
                "description": "Analyzes sales trends by comparing actual sales against forecasts",
                "inputs": ["store_ids", "product_ids", "analysis_days"],
                "outputs": ["trend_analysis (in-trend/average/slow-moving/no-trend)"]
            },
            {
                "name": "Inventory Agent",
                "description": "Assesses current inventory status and identifies stock issues",
                "inputs": ["store_ids", "product_ids", "demand_forecasts"],
                "outputs": ["inventory_status (understocked/in-stock/overstocked)"]
            },
            {
                "name": "Replenishment Agent",
                "description": "Creates replenishment plans via inter-store transfers or manufacturer orders",
                "inputs": ["understocked_items", "overstocked_items", "transfer_routes"],
                "outputs": ["replenishment_plans"]
            },
            {
                "name": "Pricing Agent",
                "description": "Generates pricing and promotion recommendations based on inventory and trends",
                "inputs": ["inventory_status", "trend_analysis"],
                "outputs": ["pricing_recommendations"]
            },
            {
                "name": "Campaign Agent",
                "description": "Creates marketing campaign creatives using AI image generation",
                "inputs": ["products", "campaign_type", "promotion_details"],
                "outputs": ["campaign_creatives (images)"]
            }
        ]
    }

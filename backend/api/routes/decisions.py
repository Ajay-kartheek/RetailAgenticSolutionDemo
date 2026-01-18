"""
Decision Routes - Human-in-the-Loop Approval System
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared.db import DynamoDBClient
from shared.models import DecisionStatus

router = APIRouter()
db = DynamoDBClient()


class DecisionAction(BaseModel):
    """Model for decision approval/rejection."""
    notes: Optional[str] = None


@router.get("")
async def list_decisions(
    status: Optional[str] = None,
    decision_type: Optional[str] = None,
    store_id: Optional[str] = None
):
    """Get all decisions with optional filters."""
    decisions = db.get_all_decisions()

    if status:
        try:
            DecisionStatus(status)  # Validate
            decisions = [d for d in decisions if d.get("status") == status]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Valid values: {[s.value for s in DecisionStatus]}"
            )

    if decision_type:
        decisions = [d for d in decisions if d.get("decision_type") == decision_type]

    if store_id:
        decisions = [d for d in decisions if d.get("store_id") == store_id]

    # Sort by timestamp descending (most recent first)
    decisions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

    return {"decisions": decisions, "count": len(decisions)}


@router.get("/pending")
async def get_pending_decisions():
    """Get all pending decisions requiring approval."""
    decisions = db.get_pending_decisions()

    # Group by decision type
    by_type = {}
    for d in decisions:
        dtype = d.get("decision_type", "unknown")
        if dtype not in by_type:
            by_type[dtype] = []
        by_type[dtype].append(d)

    return {
        "decisions": decisions,
        "count": len(decisions),
        "by_type": {k: len(v) for k, v in by_type.items()}
    }


@router.get("/summary")
async def get_decisions_summary():
    """Get summary of decisions by status."""
    decisions = db.get_all_decisions()

    summary = {
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "executed": 0,
        "total": len(decisions)
    }

    for d in decisions:
        status = d.get("status", "pending")
        if status in summary:
            summary[status] += 1

    return summary


@router.get("/{decision_id}")
async def get_decision(decision_id: str):
    """Get a specific decision by ID."""
    decision = db.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")
    return decision


@router.post("/{decision_id}/approve")
async def approve_decision(decision_id: str, action: DecisionAction = None):
    """Approve a pending decision."""
    decision = db.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    if decision.get("status") != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Decision is not pending. Current status: {decision.get('status')}"
        )

    # Update decision
    updates = {
        "status": "approved",
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "approved_by": "user"  # In production, would get from auth
    }

    if action and action.notes:
        updates["approval_notes"] = action.notes

    db.update_decision(decision_id, updates)

    # Trigger Agent Execution (Synchronous for UI feedback)
    try:
        from agents.orchestrator import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        
        # Pass the full decision data which contains the plan
        execution_result = orchestrator.execute_decision(
            decision_id=decision_id,
            decision_type=decision.get("decision_type", ""),
            data=decision.get("data", {})
        )
        
        # Update decision with execution results
        exec_updates = {
            "status": "executed",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "execution_result": execution_result
        }
        db.update_decision(decision_id, exec_updates)
        
        return {
            "message": f"Decision {decision_id} approved and executed successfully",
            "decision_id": decision_id,
            "status": "executed",
            "execution_result": execution_result
        }
        
    except Exception as e:
        # If execution fails, we still leave it as approved but log error
        print(f"Error executing decision {decision_id}: {e}")
        return {
            "message": f"Decision approved but execution failed: {str(e)}",
            "decision_id": decision_id,
            "status": "approved_with_error"
        }


@router.post("/{decision_id}/reject")
async def reject_decision(decision_id: str, action: DecisionAction = None):
    """Reject a pending decision."""
    decision = db.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    if decision.get("status") != "pending":
        raise HTTPException(
            status_code=400,
            detail=f"Decision is not pending. Current status: {decision.get('status')}"
        )

    # Update decision
    updates = {
        "status": "rejected",
        "rejected_at": datetime.now(timezone.utc).isoformat(),
        "rejected_by": "user"
    }

    if action and action.notes:
        updates["rejection_notes"] = action.notes

    db.update_decision(decision_id, updates)

    return {
        "message": f"Decision {decision_id} rejected",
        "decision_id": decision_id,
        "status": "rejected"
    }


@router.post("/{decision_id}/execute")
async def execute_decision(decision_id: str):
    """Mark an approved decision as executed."""
    decision = db.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    if decision.get("status") != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Decision must be approved before execution. Current status: {decision.get('status')}"
        )

    # Update decision
    updates = {
        "status": "executed",
        "executed_at": datetime.now(timezone.utc).isoformat()
    }

    db.update_decision(decision_id, updates)

    return {
        "message": f"Decision {decision_id} marked as executed",
        "decision_id": decision_id,
        "status": "executed"
    }


@router.post("/{decision_id}/receive")
async def receive_decision_products(decision_id: str):
    """
    Receive stock for an executed decision (e.g., transfer arrival).
    """
    decision = db.get_decision(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail=f"Decision {decision_id} not found")

    if decision.get("status") != "executed":
        raise HTTPException(
            status_code=400,
            detail=f"Decision must be executed (in transit) before receiving. Current status: {decision.get('status')}"
        )
    
    # Check if already received
    exec_result = decision.get("execution_result", {})
    if exec_result.get("fulfillment_status") == "received":
         return {
            "message": "Stock already received.",
            "decision_id": decision_id,
            "status": "executed",
            "fulfillment_status": "received"
        }

    # Trigger Agent to Receive
    try:
        from agents.replenishment_agent.agent import ReplenishmentAgent
        agent = ReplenishmentAgent()
        
        # Use data from decision
        receive_result = agent.receive_transfer(decision.get("data", {}))
        
        # Update decision with reception info
        # We merge execution_result or wrap it?
        # Let's update the execution_result with new status
        updates = {
            "execution_result": {**exec_result, **receive_result},
            "received_at": datetime.now(timezone.utc).isoformat()
        }
        
        db.update_decision(decision_id, updates)
        
        return {
            "message": f"Stock received for decision {decision_id}",
            "decision_id": decision_id,
            "status": "executed",
            "fulfillment_status": "received",
            "result": receive_result
        }
        
    except Exception as e:
        print(f"Error receiving stock for {decision_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

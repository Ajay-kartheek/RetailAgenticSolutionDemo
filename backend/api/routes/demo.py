"""
Demo seeder API routes.
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class SeedRequest(BaseModel):
    scenario: int = 4


class SeedResponse(BaseModel):
    status: str
    scenario: int
    scenario_name: str
    message: str


@router.post("/seed", response_model=SeedResponse)
async def seed_demo_data(request: SeedRequest):
    """
    Seed demo data for a given scenario.
    Clears existing data and populates with the chosen scenario.
    """
    if request.scenario not in [1, 2, 3, 4]:
        raise HTTPException(status_code=400, detail="Scenario must be 1, 2, 3, or 4")

    try:
        # Import here to avoid circular imports and module-level side effects
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from demo_seeder import seed_scenario, SCENARIO_1, SCENARIO_2, SCENARIO_3, SCENARIO_4

        scenarios = {1: SCENARIO_1, 2: SCENARIO_2, 3: SCENARIO_3, 4: SCENARIO_4}
        scenario_data = scenarios[request.scenario]

        logger.info(f"Seeding scenario {request.scenario}: {scenario_data['name']}")
        seed_scenario(request.scenario)
        logger.info(f"Scenario {request.scenario} seeded successfully")

        return SeedResponse(
            status="success",
            scenario=request.scenario,
            scenario_name=scenario_data["name"],
            message=f"Successfully seeded scenario {request.scenario}: {scenario_data['name']}",
        )
    except Exception as e:
        logger.error(f"Error seeding scenario {request.scenario}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to seed data: {str(e)}")


@router.post("/clear")
async def clear_demo_data():
    """Clear all demo data from tables."""
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from demo_seeder import clear_all_data

        logger.info("Clearing all demo data")
        clear_all_data()
        logger.info("Demo data cleared successfully")

        return {"status": "success", "message": "All demo data cleared"}
    except Exception as e:
        logger.error(f"Error clearing data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")

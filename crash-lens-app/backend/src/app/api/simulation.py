from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..services.simulation_service import SimulationService
from ..schema.simulation import SimulateCrashRequest, SimulateCrashResponse
from ..core.database import get_db

router = APIRouter()


@router.post("/simulate-crash", response_model=SimulateCrashResponse)
def simulate_crash(
    request: SimulateCrashRequest, background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Simulate a crash scenario and generate realistic logs.

    This endpoint simulates various crash scenarios including:
    - Payment gateway timeouts
    - Database migration errors
    - Inventory oversell detection
    - Payment verification timeouts
    - Database startup failures
    - Stripe signature verification errors

    The simulation generates realistic log entries and creates a crash record
    in the database with the specified repository association.
    """
    try:
        simulation_service = SimulationService(db)
        result = simulation_service.simulate_crash(request, background_tasks)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid simulation request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

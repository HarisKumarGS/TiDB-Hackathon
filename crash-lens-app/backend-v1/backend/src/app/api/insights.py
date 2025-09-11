from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services.insights_service import InsightsService
from ..services.repository_service import RepositoryService
from ..schema.insights import InsightsResponse
from ..core.database import get_db

router = APIRouter()


@router.get("/insights/{repository_id}", response_model=InsightsResponse)
def get_insights(repository_id: str, db: Session = Depends(get_db)):
    """
    Get comprehensive insights about crashes and issues for a specific repository.

    - **repository_id**: The unique identifier of the repository

    Returns:
    - Total number of crashes, critical issues, and affected users for the repository
    - Number of issues resolved today for the repository
    - Crashes from past 3 days for the repository
    - Weekly crash vs resolved data for past 4 weeks for the repository
    - Crash breakdown by severity (Critical, High, Medium, Low) for the repository
    - Component breakdown sorted by crash count for the repository
    """
    try:
        # First check if repository exists
        repository_service = RepositoryService(db)
        repository = repository_service.get_repository(repository_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        insights_service = InsightsService(db)
        insights = insights_service.get_insights(repository_id)
        return insights
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate insights: {str(e)}"
        )

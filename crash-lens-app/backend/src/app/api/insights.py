from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ..services.insights_service import InsightsService
from ..schema.insights import InsightsResponse
from ..core.database import get_db

router = APIRouter()


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive insights about crashes and issues.
    
    Returns:
    - Total number of crashes, critical issues, and affected users
    - Number of issues resolved today
    - Crashes from past 3 days
    - Weekly crash vs resolved data for past 4 weeks
    - Crash breakdown by severity (Critical, High, Medium, Low)
    - Component breakdown sorted by crash count
    """
    try:
        insights_service = InsightsService(db)
        insights = await insights_service.get_insights()
        return insights
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate insights: {str(e)}"
        )

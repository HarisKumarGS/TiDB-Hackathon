from fastapi import APIRouter
from ..services.slack_service import SlackService

router = APIRouter()


@router.get("/slack-status")
async def get_slack_status():
    """Get Slack service status and configuration"""
    slack_service = SlackService()
    return slack_service.get_channel_info()


@router.get("/services-status")
async def get_all_services_status():
    """Get status of all external services"""
    slack_service = SlackService()

    return {
        "slack": slack_service.get_channel_info(),
        "overall_status": "healthy" if slack_service.is_available() else "degraded",
    }

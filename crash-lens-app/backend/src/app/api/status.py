from fastapi import APIRouter
from ..services.s3_service import S3Service
from ..services.slack_service import SlackService

router = APIRouter()


@router.get("/s3-status")
async def get_s3_status():
    """Get S3 service status and configuration"""
    s3_service = S3Service()
    return s3_service.get_bucket_info()


@router.get("/slack-status")
async def get_slack_status():
    """Get Slack service status and configuration"""
    slack_service = SlackService()
    return slack_service.get_channel_info()


@router.get("/services-status")
async def get_all_services_status():
    """Get status of all external services"""
    s3_service = S3Service()
    slack_service = SlackService()

    return {
        "s3": s3_service.get_bucket_info(),
        "slack": slack_service.get_channel_info(),
        "overall_status": "healthy"
        if s3_service.is_available() and slack_service.is_available()
        else "degraded",
    }

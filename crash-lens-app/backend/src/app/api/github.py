from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from ..core.database import get_db
from ..services.github_service import GitHubService


router = APIRouter(prefix="/github", tags=["GitHub"])


class CreatePullRequestRequest(BaseModel):
    crash_rca_id: str


class PullRequestStatusRequest(BaseModel):
    owner: str
    repo_name: str
    pr_number: int


@router.post("/create-pull-request", response_model=Dict[str, Any])
async def create_pull_request(
    request: CreatePullRequestRequest,
    db: Session = Depends(get_db)
):
    """
    Create a GitHub pull request from crash RCA data
    
    This endpoint:
    1. Gets crash RCA data and associated repository information
    2. Retrieves git diff from the git_diff field in crash_rca table
    3. Clones the repository, applies the diff, and creates a new branch
    4. Creates a pull request with detailed information about the crash and fix
    """
    try:
        github_service = GitHubService(db)
        
        if not github_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub service is not available. Please check GITHUB_TOKEN configuration."
            )
        
        result = github_service.create_pull_request_from_crash_rca(request.crash_rca_id)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "message": "Pull request created successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/pull-request-status", response_model=Dict[str, Any])
async def get_pull_request_status(
    request: PullRequestStatusRequest,
    db: Session = Depends(get_db)
):
    """
    Get the status of a GitHub pull request
    
    Returns detailed information about the pull request including:
    - Current status (open, closed, merged)
    - Merge status and conflicts
    - Statistics (comments, commits, additions, deletions)
    - Timestamps and author information
    """
    try:
        github_service = GitHubService(db)
        
        if not github_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="GitHub service is not available. Please check GITHUB_TOKEN configuration."
            )
        
        result = github_service.get_pull_request_status(
            request.owner, 
            request.repo_name, 
            request.pr_number
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return {
            "message": "Pull request status retrieved successfully",
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/service-info", response_model=Dict[str, Any])
async def get_github_service_info(db: Session = Depends(get_db)):
    """
    Get information about the GitHub service configuration
    
    Returns:
    - Service availability status
    - Authenticated user information
    - Rate limit information
    """
    try:
        github_service = GitHubService(db)
        service_info = github_service.get_service_info()
        
        return {
            "message": "GitHub service information retrieved successfully",
            "data": service_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, Any])
async def github_service_health(db: Session = Depends(get_db)):
    """
    Health check endpoint for GitHub service
    
    Returns basic availability status without detailed information
    """
    try:
        github_service = GitHubService(db)
        is_available = github_service.is_available()
        
        return {
            "status": "healthy" if is_available else "unavailable",
            "github_available": is_available
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "github_available": False
        }

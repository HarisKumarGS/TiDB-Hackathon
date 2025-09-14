from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import logging

from ..core.database import get_db
from ..services.github_service import github_service
from ..models.sqlalchemy_models import CrashRCA

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/github", tags=["github"])


@router.post("/create-pr/{crash_rca_id}")
async def create_pull_request(
    crash_rca_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Create a pull request from a crash RCA.
    
    Args:
        crash_rca_id: The ID of the crash RCA record
        db: Database session dependency
        
    Returns:
        Dict containing PR creation status and details
    """
    try:
        # Validate that the RCA exists
        rca = db.query(CrashRCA).filter(CrashRCA.id == crash_rca_id).first()
        if not rca:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crash RCA with ID {crash_rca_id} not found"
            )
        
        # Validate that git_diff exists
        if not rca.git_diff:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No git diff found in RCA data. Cannot create pull request."
            )
        
        # Create pull request using the GitHub service
        result = await github_service.create_pull_request_from_rca(crash_rca_id, db)
        
        # Store the PR URL in the database
        if result.get("status") == "success" and result.get("pr_url"):
            rca.pull_request_url = result["pr_url"]
            db.commit()
            logger.info(f"Stored PR URL in database for RCA {crash_rca_id}: {result['pr_url']}")
        
        logger.info(f"Successfully created PR for RCA {crash_rca_id}: {result.get('pr_url')}")
        
        return {
            "message": "Pull request created successfully",
            "crash_rca_id": crash_rca_id,
            "pr_details": result
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        # Handle validation errors
        logger.error(f"Validation error for RCA {crash_rca_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error creating PR for RCA {crash_rca_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create pull request: {str(e)}"
        )


@router.get("/pr-status/{crash_rca_id}")
async def get_pr_status(
    crash_rca_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get the status of a pull request for a given crash RCA.
    
    Args:
        crash_rca_id: The ID of the crash RCA record
        db: Database session dependency
        
    Returns:
        Dict containing PR status information
    """
    try:
        # Validate that the RCA exists
        rca = db.query(CrashRCA).filter(CrashRCA.id == crash_rca_id).first()
        if not rca:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crash RCA with ID {crash_rca_id} not found"
            )
        
        # Return status including existing PR URL if available
        return {
            "crash_rca_id": crash_rca_id,
            "has_git_diff": bool(rca.git_diff),
            "can_create_pr": bool(rca.git_diff) and not rca.pull_request_url,
            "pull_request_url": rca.pull_request_url,
            "message": "Pull request already exists" if rca.pull_request_url else "Use POST /github/create-pr/{crash_rca_id} to create a pull request"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting PR status for RCA {crash_rca_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get PR status: {str(e)}"
        )


@router.post("/validate-diff/{crash_rca_id}")
async def validate_git_diff(
    crash_rca_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Validate the git diff in a crash RCA without creating a PR.
    
    Args:
        crash_rca_id: The ID of the crash RCA record
        db: Database session dependency
        
    Returns:
        Dict containing validation results
    """
    try:
        # Validate that the RCA exists
        rca = db.query(CrashRCA).filter(CrashRCA.id == crash_rca_id).first()
        if not rca:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crash RCA with ID {crash_rca_id} not found"
            )
        
        if not rca.git_diff:
            return {
                "crash_rca_id": crash_rca_id,
                "is_valid": False,
                "error": "No git diff found in RCA data",
                "can_create_pr": False
            }
        
        try:
            # Try to parse the diff using the GitHub service
            patch_set = github_service._parse_diff_with_unidiff(rca.git_diff)
            
            return {
                "crash_rca_id": crash_rca_id,
                "is_valid": True,
                "files_count": len(patch_set),
                "files": [pf.path for pf in patch_set],
                "can_create_pr": True,
                "message": "Git diff is valid and ready for PR creation"
            }
            
        except Exception as parse_error:
            return {
                "crash_rca_id": crash_rca_id,
                "is_valid": False,
                "error": str(parse_error),
                "can_create_pr": False
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating diff for RCA {crash_rca_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate git diff: {str(e)}"
        )

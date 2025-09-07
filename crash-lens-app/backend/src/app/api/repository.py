from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from ..services.repository_service import RepositoryService
from ..schema.repository import (
    RepositoryCreate, 
    RepositoryUpdate, 
    Repository, 
    RepositoryResponse, 
    RepositoryListResponse
)
from ..core.database import get_db

router = APIRouter()


@router.post("/repositories", response_model=RepositoryResponse)
async def create_repository(
    repository_data: RepositoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new repository.
    
    This endpoint creates a new repository with the provided name and URL.
    The repository ID will be automatically generated.
    """
    try:
        repository_service = RepositoryService(db)
        repository = await repository_service.create_repository(repository_data)
        
        return RepositoryResponse(
            success=True,
            message="Repository created successfully",
            data=repository
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create repository: {str(e)}"
        )


@router.get("/repositories", response_model=RepositoryListResponse)
async def get_repositories(
    skip: int = Query(0, ge=0, description="Number of repositories to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of repositories to return"),
    search: Optional[str] = Query(None, description="Search term for repository name or URL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all repositories with optional search and pagination.
    
    - **skip**: Number of repositories to skip (for pagination)
    - **limit**: Maximum number of repositories to return (1-1000)
    - **search**: Optional search term to filter by name or URL
    """
    try:
        repository_service = RepositoryService(db)
        
        if search:
            repositories = await repository_service.search_repositories(search, skip, limit)
        else:
            repositories = await repository_service.get_repositories(skip, limit)
        
        total = await repository_service.get_repository_count()
        
        return RepositoryListResponse(
            success=True,
            message=f"Retrieved {len(repositories)} repositories",
            data=repositories,
            total=total
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve repositories: {str(e)}"
        )


@router.get("/repositories/{repository_id}", response_model=RepositoryResponse)
async def get_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific repository by ID.
    
    - **repository_id**: The unique identifier of the repository
    """
    try:
        repository_service = RepositoryService(db)
        repository = await repository_service.get_repository(repository_id)
        
        if not repository:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        
        return RepositoryResponse(
            success=True,
            message="Repository retrieved successfully",
            data=repository
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve repository: {str(e)}"
        )


@router.put("/repositories/{repository_id}", response_model=RepositoryResponse)
async def update_repository(
    repository_id: str,
    update_data: RepositoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a repository.
    
    - **repository_id**: The unique identifier of the repository
    - **update_data**: The fields to update (name and/or url)
    """
    try:
        repository_service = RepositoryService(db)
        repository = await repository_service.update_repository(repository_id, update_data)
        
        if not repository:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        
        return RepositoryResponse(
            success=True,
            message="Repository updated successfully",
            data=repository
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update repository: {str(e)}"
        )


@router.delete("/repositories/{repository_id}", response_model=RepositoryResponse)
async def delete_repository(
    repository_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a repository.
    
    - **repository_id**: The unique identifier of the repository
    
    Note: This will also delete all associated crashes due to CASCADE constraint.
    """
    try:
        repository_service = RepositoryService(db)
        success = await repository_service.delete_repository(repository_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        
        return RepositoryResponse(
            success=True,
            message="Repository deleted successfully",
            data=None
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete repository: {str(e)}"
        )

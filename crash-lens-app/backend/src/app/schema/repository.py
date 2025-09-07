from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RepositoryBase(BaseModel):
    """Base repository schema with common fields"""
    name: str = Field(..., max_length=255, description="Repository name")
    url: str = Field(..., max_length=255, description="Repository URL")


class RepositoryCreate(RepositoryBase):
    """Schema for creating a new repository"""
    pass


class RepositoryUpdate(BaseModel):
    """Schema for updating a repository"""
    name: Optional[str] = Field(None, max_length=255, description="Repository name")
    url: Optional[str] = Field(None, max_length=255, description="Repository URL")


class Repository(RepositoryBase):
    """Complete repository schema with ID and optional timestamps"""
    id: str = Field(..., description="Repository unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        from_attributes = True


class RepositoryResponse(BaseModel):
    """Response schema for repository operations"""
    success: bool
    message: str
    data: Optional[Repository] = None


class RepositoryListResponse(BaseModel):
    """Response schema for listing repositories"""
    success: bool
    message: str
    data: list[Repository] = Field(default_factory=list)
    total: int = 0

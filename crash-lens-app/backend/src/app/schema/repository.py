from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RepositoryBase(BaseModel):
    """Base repository schema with common fields"""

    name: str = Field(..., max_length=255, description="Repository name")
    url: str = Field(..., max_length=255, description="Repository URL")
    document_url: Optional[str] = Field(None, max_length=500, description="Documentation URL")


class RepositoryCreate(RepositoryBase):
    """Schema for creating a new repository"""

    pass


class RepositoryUpdate(BaseModel):
    """Schema for updating a repository"""

    name: Optional[str] = Field(None, max_length=255, description="Repository name")
    url: Optional[str] = Field(None, max_length=255, description="Repository URL")
    document_url: Optional[str] = Field(None, max_length=500, description="Documentation URL")


class Repository(RepositoryBase):
    """Complete repository schema with ID and timestamps"""

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


class Crash(BaseModel):
    """Crash schema for repository crashes"""

    id: str = Field(..., description="Crash unique identifier")
    component: str = Field(
        ..., max_length=255, description="Component where crash occurred"
    )
    error_type: str = Field(..., max_length=255, description="Type of error")
    severity: str = Field(..., max_length=50, description="Severity level")
    status: str = Field(..., max_length=50, description="Current status")
    impacted_users: int = Field(..., description="Number of users impacted")
    comment: Optional[str] = Field(
        None, max_length=500, description="Additional comments"
    )
    error_log: Optional[str] = Field(
        None, description="URL to error log file"
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class RepositoryCrashesResponse(BaseModel):
    """Response schema for repository crashes"""

    success: bool
    message: str
    data: List[Crash] = Field(default_factory=list)
    total: int = 0


class CrashUpdate(BaseModel):
    """Schema for updating a crash"""

    status: Optional[str] = Field(
        None, max_length=50, description="New status of the crash"
    )
    comment: Optional[str] = Field(
        None, max_length=500, description="Additional comment or notes"
    )


class CrashResponse(BaseModel):
    """Response schema for crash operations"""

    success: bool
    message: str
    data: Optional[Crash] = None


class CrashRCA(BaseModel):
    """Crash RCA schema"""

    id: str = Field(..., description="RCA unique identifier")
    crash_id: str = Field(..., description="Associated crash ID")
    description: Optional[str] = Field(None, description="RCA description")
    problem_identification: Optional[str] = Field(
        None, description="Problem identification details"
    )
    data_collection: Optional[str] = Field(None, description="Data collection process")
    root_cause_identification: Optional[str] = Field(
        None, description="Root cause identification"
    )
    solution: Optional[str] = Field(None, description="Proposed solution")
    author: Optional[List[str]] = Field(None, description="RCA authors")
    supporting_documents: Optional[List[str]] = Field(
        None, description="Supporting document URLs"
    )
    git_diff: Optional[str] = Field(
        None, description="Git Diff of the Solution"
    )
    pull_request_url: Optional[str] = Field(
        None, max_length=500, description="GitHub Pull Request URL"
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class CrashWithRCA(BaseModel):
    """Combined crash and RCA data schema"""
    
    # Crash data
    crash: Crash
    # RCA data (optional since RCA might not exist)
    rca: Optional[CrashRCA] = None

    class Config:
        from_attributes = True


class CrashRCAResponse(BaseModel):
    """Response schema for RCA operations"""

    success: bool
    message: str
    data: Optional[CrashRCA] = None


class CrashRCAUpdate(BaseModel):
    """Schema for updating RCA data"""

    description: Optional[str] = Field(None, description="RCA description")
    problem_identification: Optional[str] = Field(
        None, description="Problem identification details"
    )
    data_collection: Optional[str] = Field(None, description="Data collection process")
    root_cause_identification: Optional[str] = Field(
        None, description="Root cause identification"
    )
    solution: Optional[str] = Field(None, description="Proposed solution")
    author: Optional[List[str]] = Field(None, description="RCA authors")
    supporting_documents: Optional[List[str]] = Field(
        None, description="Supporting document URLs"
    )
    git_diff: Optional[str] = Field(
        None, description="Git Diff of the Solution"
    )
    pull_request_url: Optional[str] = Field(
        None, max_length=500, description="GitHub Pull Request URL"
    )


class CrashWithRCAResponse(BaseModel):
    """Response schema for combined crash and RCA operations"""

    success: bool
    message: str
    data: Optional[CrashWithRCA] = None

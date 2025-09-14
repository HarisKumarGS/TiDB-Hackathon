from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Repository(BaseModel):
    """Repository model"""

    id: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    url: str = Field(..., max_length=255)
    document_url: Optional[str] = Field(None, max_length=500, description="Documentation URL")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class Crash(BaseModel):
    """Crash model"""

    id: str
    component: str = Field(..., max_length=255)
    error_type: str = Field(..., max_length=255)
    severity: str = Field(..., max_length=50)
    status: str = Field(..., max_length=50)
    impacted_users: int
    comment: Optional[str] = Field(None, max_length=500)
    repository_id: str
    error_log: Optional[str] = Field(
        None, description="Error log content stored as longtext"
    )
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class CrashRCA(BaseModel):
    """Crash RCA model"""

    id: str
    crash_id: str
    description: Optional[str] = None
    problem_identification: Optional[str] = None
    data_collection: Optional[str] = None
    root_cause_identification: Optional[str] = None
    solution: Optional[str] = None
    author: Optional[List[str]] = None
    supporting_documents: Optional[List[str]] = None
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

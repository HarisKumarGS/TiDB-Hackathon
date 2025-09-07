from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class WeeklyCrashData(BaseModel):
    """Weekly crash data for past 4 weeks"""
    week: str  # Week identifier (e.g., "Week 1", "Week 2")
    crashes: int
    resolved: int


class SeverityCount(BaseModel):
    """Crash count by severity"""
    critical: int
    high: int
    medium: int
    low: int


class ComponentCount(BaseModel):
    """Component crash count"""
    component: str
    count: int


class InsightsResponse(BaseModel):
    """Insights API response schema"""
    # Basic counts
    total_crashes: int
    critical_issues: int
    affected_users: int
    
    # Today's resolved issues
    resolved_today: int
    
    # Past 3 days crashes
    crashes_past_3_days: int
    
    # Past 4 weeks data
    weekly_data: List[WeeklyCrashData]
    
    # Severity breakdown
    severity_breakdown: SeverityCount
    
    # Component breakdown (sorted by count descending)
    component_breakdown: List[ComponentCount]
    
    # Metadata
    generated_at: datetime

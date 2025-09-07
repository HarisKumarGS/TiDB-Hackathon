from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from sqlalchemy import text
from ..models.model import Crash, CrashRCA
from ..schema.insights import (
    InsightsResponse, 
    WeeklyCrashData, 
    SeverityCount, 
    ComponentCount
)


class InsightsService:
    """Service for generating insights data"""
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def get_insights(self) -> InsightsResponse:
        """Generate comprehensive insights data"""
        
        # Get basic counts
        total_crashes = await self._get_total_crashes()
        critical_issues = await self._get_critical_issues()
        affected_users = await self._get_total_affected_users()
        
        # Get today's resolved issues
        resolved_today = await self._get_resolved_today()
        
        # Get past 3 days crashes
        crashes_past_3_days = await self._get_crashes_past_3_days()
        
        # Get weekly data for past 4 weeks
        weekly_data = await self._get_weekly_data()
        
        # Get severity breakdown
        severity_breakdown = await self._get_severity_breakdown()
        
        # Get component breakdown
        component_breakdown = await self._get_component_breakdown()
        
        return InsightsResponse(
            total_crashes=total_crashes,
            critical_issues=critical_issues,
            affected_users=affected_users,
            resolved_today=resolved_today,
            crashes_past_3_days=crashes_past_3_days,
            weekly_data=weekly_data,
            severity_breakdown=severity_breakdown,
            component_breakdown=component_breakdown,
            generated_at=datetime.now()
        )
    
    async def _get_total_crashes(self) -> int:
        """Get total number of crashes"""
        query = text("SELECT COUNT(*) as count FROM crash")
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _get_critical_issues(self) -> int:
        """Get total number of critical issues"""
        query = text("SELECT COUNT(*) as count FROM crash WHERE severity = 'critical'")
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _get_total_affected_users(self) -> int:
        """Get total number of affected users"""
        query = text("SELECT SUM(impacted_users) as total FROM crash")
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def _get_resolved_today(self) -> int:
        """Get number of issues resolved today"""
        today = datetime.now().date()
        query = text("""
            SELECT COUNT(*) as count 
            FROM crash 
            WHERE status = 'resolved' 
            AND DATE(updated_at) = :today
        """)
        result = await self.db.execute(query, {"today": today})
        return result.scalar() or 0
    
    async def _get_crashes_past_3_days(self) -> int:
        """Get crashes from past 3 days"""
        three_days_ago = datetime.now().date() - timedelta(days=3)
        query = text("""
            SELECT COUNT(*) as count 
            FROM crash 
            WHERE DATE(created_at) >= :three_days_ago
        """)
        result = await self.db.execute(query, {"three_days_ago": three_days_ago})
        return result.scalar() or 0
    
    async def _get_weekly_data(self) -> List[WeeklyCrashData]:
        """Get weekly crash data for past 4 weeks"""
        weekly_data = []
        
        for week_num in range(4, 0, -1):  # Past 4 weeks
            week_start = datetime.now().date() - timedelta(weeks=week_num)
            week_end = week_start + timedelta(days=6)
            
            # Get crashes for this week
            crashes_query = text("""
                SELECT COUNT(*) as count 
                FROM crash 
                WHERE DATE(created_at) BETWEEN :week_start AND :week_end
            """)
            crashes_result = await self.db.execute(crashes_query, {
                "week_start": week_start,
                "week_end": week_end
            })
            crashes_count = crashes_result.scalar() or 0
            
            # Get resolved crashes for this week
            resolved_query = text("""
                SELECT COUNT(*) as count 
                FROM crash 
                WHERE status = 'resolved' 
                AND DATE(updated_at) BETWEEN :week_start AND :week_end
            """)
            resolved_result = await self.db.execute(resolved_query, {
                "week_start": week_start,
                "week_end": week_end
            })
            resolved_count = resolved_result.scalar() or 0
            
            weekly_data.append(WeeklyCrashData(
                week=f"Week {5 - week_num}",
                crashes=crashes_count,
                resolved=resolved_count
            ))
        
        return weekly_data
    
    async def _get_severity_breakdown(self) -> SeverityCount:
        """Get crash count by severity"""
        query = text("""
            SELECT 
                SUM(CASE WHEN severity = 'critical' THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low
            FROM crash
        """)
        result = await self.db.execute(query)
        row = result.fetchone()
        
        return SeverityCount(
            critical=row.critical or 0,
            high=row.high or 0,
            medium=row.medium or 0,
            low=row.low or 0
        )
    
    async def _get_component_breakdown(self) -> List[ComponentCount]:
        """Get component breakdown sorted by count descending"""
        query = text("""
            SELECT component, COUNT(*) as count 
            FROM crash 
            GROUP BY component 
            ORDER BY count DESC
        """)
        result = await self.db.execute(query)
        
        return [
            ComponentCount(component=row.component, count=row.count)
            for row in result.fetchall()
        ]

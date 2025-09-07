import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from ..models.model import Repository
from ..schema.repository import RepositoryCreate, RepositoryUpdate, Crash, CrashUpdate
from ..utils.datetime_utils import get_utc_now_naive


class RepositoryService:
    """Service for repository management operations"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    async def create_repository(self, repository_data: RepositoryCreate) -> Repository:
        """Create a new repository"""
        repository_id = str(uuid.uuid4())
        now = get_utc_now_naive()
        
        query = text("""
            INSERT INTO repository (id, name, url, created_at, updated_at)
            VALUES (:id, :name, :url, :created_at, :updated_at)
            RETURNING id, name, url, created_at, updated_at
        """)
        
        result = await self.db.execute(query, {
            "id": repository_id,
            "name": repository_data.name,
            "url": repository_data.url,
            "created_at": now,
            "updated_at": now
        })
        
        await self.db.commit()
        row = result.fetchone()
        
        return Repository(
            id=row.id,
            name=row.name,
            url=row.url,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive()
        )
    
    async def get_repository(self, repository_id: str) -> Optional[Repository]:
        """Get a repository by ID"""
        query = text("""
            SELECT id, name, url, created_at, updated_at
            FROM repository
            WHERE id = :id
        """)
        
        result = await self.db.execute(query, {"id": repository_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return Repository(
            id=row.id,
            name=row.name,
            url=row.url,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive()
        )
    
    async def get_repositories(self, skip: int = 0, limit: int = 100) -> List[Repository]:
        """Get all repositories with pagination"""
        query = text("""
            SELECT id, name, url, created_at, updated_at
            FROM repository
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = await self.db.execute(query, {"skip": skip, "limit": limit})
        rows = result.fetchall()
        
        return [
            Repository(
                id=row.id,
                name=row.name,
                url=row.url,
                created_at=row.created_at or get_utc_now_naive(),
                updated_at=row.updated_at or get_utc_now_naive()
            )
            for row in rows
        ]
    
    async def update_repository(self, repository_id: str, update_data: RepositoryUpdate) -> Optional[Repository]:
        """Update a repository"""
        # First check if repository exists
        existing = await self.get_repository(repository_id)
        if not existing:
            return None
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = {"id": repository_id, "updated_at": get_utc_now_naive()}
        
        if update_data.name is not None:
            update_fields.append("name = :name")
            params["name"] = update_data.name
        
        if update_data.url is not None:
            update_fields.append("url = :url")
            params["url"] = update_data.url
        
        if not update_fields:
            return existing  # No fields to update
        
        query = text(f"""
            UPDATE repository
            SET {', '.join(update_fields)}, updated_at = :updated_at
            WHERE id = :id
            RETURNING id, name, url, created_at, updated_at
        """)
        
        result = await self.db.execute(query, params)
        await self.db.commit()
        row = result.fetchone()
        
        return Repository(
            id=row.id,
            name=row.name,
            url=row.url,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive()
        )
    
    async def delete_repository(self, repository_id: str) -> bool:
        """Delete a repository"""
        # First check if repository exists
        existing = await self.get_repository(repository_id)
        if not existing:
            return False
        
        query = text("DELETE FROM repository WHERE id = :id")
        await self.db.execute(query, {"id": repository_id})
        await self.db.commit()
        
        return True
    
    async def get_repository_count(self) -> int:
        """Get total count of repositories"""
        query = text("SELECT COUNT(*) as count FROM repository")
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_repository_crashes(self, repository_id: str, skip: int = 0, limit: int = 100) -> List[Crash]:
        """Get all crashes for a specific repository with pagination"""
        query = text("""
            SELECT id, component, error_type, severity, status, impacted_users, 
                   comment, error_log, created_at, updated_at
            FROM crash
            WHERE repository_id = :repository_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = await self.db.execute(query, {
            "repository_id": repository_id,
            "skip": skip,
            "limit": limit
        })
        rows = result.fetchall()
        
        return [
            Crash(
                id=row.id,
                component=row.component,
                error_type=row.error_type,
                severity=row.severity,
                status=row.status,
                impacted_users=row.impacted_users,
                comment=row.comment,
                error_log=row.error_log,
                created_at=row.created_at or get_utc_now_naive(),
                updated_at=row.updated_at or get_utc_now_naive()
            )
            for row in rows
        ]
    
    async def get_repository_crash_count(self, repository_id: str) -> int:
        """Get total count of crashes for a specific repository"""
        query = text("SELECT COUNT(*) as count FROM crash WHERE repository_id = :repository_id")
        result = await self.db.execute(query, {"repository_id": repository_id})
        return result.scalar() or 0
    
    async def get_crash(self, crash_id: str) -> Optional[Crash]:
        """Get a crash by ID"""
        query = text("""
            SELECT id, component, error_type, severity, status, impacted_users, 
                   comment, error_log, repository_id, created_at, updated_at
            FROM crash
            WHERE id = :id
        """)
        
        result = await self.db.execute(query, {"id": crash_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return Crash(
            id=row.id,
            component=row.component,
            error_type=row.error_type,
            severity=row.severity,
            status=row.status,
            impacted_users=row.impacted_users,
            comment=row.comment,
            error_log=row.error_log,
            repository_id=row.repository_id,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive()
        )
    
    async def update_crash(self, crash_id: str, update_data: CrashUpdate) -> Optional[Crash]:
        """Update a crash with new status and/or comment"""
        # First check if crash exists
        existing = await self.get_crash(crash_id)
        if not existing:
            return None
        
        # Build update query dynamically based on provided fields
        update_fields = []
        params = {"id": crash_id, "updated_at": get_utc_now_naive()}
        
        if update_data.status is not None:
            update_fields.append("status = :status")
            params["status"] = update_data.status
        
        if update_data.comment is not None:
            update_fields.append("comment = :comment")
            params["comment"] = update_data.comment
        
        if not update_fields:
            return existing  # No fields to update
        
        query = text(f"""
            UPDATE crash
            SET {', '.join(update_fields)}, updated_at = :updated_at
            WHERE id = :id
            RETURNING id, component, error_type, severity, status, impacted_users, 
                     comment, error_log, repository_id, created_at, updated_at
        """)
        
        result = await self.db.execute(query, params)
        await self.db.commit()
        row = result.fetchone()
        
        return Crash(
            id=row.id,
            component=row.component,
            error_type=row.error_type,
            severity=row.severity,
            status=row.status,
            impacted_users=row.impacted_users,
            comment=row.comment,
            error_log=row.error_log,
            repository_id=row.repository_id,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive()
        )
    
    async def search_repositories(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Repository]:
        """Search repositories by name or URL"""
        query = text("""
            SELECT id, name, url, created_at, updated_at
            FROM repository
            WHERE name ILIKE :search_term OR url ILIKE :search_term
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = await self.db.execute(query, {
            "search_term": f"%{search_term}%",
            "skip": skip,
            "limit": limit
        })
        rows = result.fetchall()
        
        return [
            Repository(
                id=row.id,
                name=row.name,
                url=row.url,
                created_at=row.created_at or get_utc_now_naive(),
                updated_at=row.updated_at or get_utc_now_naive()
            )
            for row in rows
        ]

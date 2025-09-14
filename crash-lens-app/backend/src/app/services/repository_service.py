import uuid
import json
from typing import List, Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text, select

from ..core.code_indexer import CodeIndexer
from ..core.document_indexer import DocumentIndexer
from ..models.model import Repository
from ..schema.repository import RepositoryCreate, RepositoryUpdate, Crash, CrashUpdate, CrashRCA, CrashRCAUpdate, CrashWithRCA
from ..utils.datetime_utils import get_utc_now_naive


class RepositoryService:
    """Service for repository management operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def _index_repository(self, id: str, url: str):
        indexer = CodeIndexer(id, url)
        indexer.index()

    def _index_documents(self, id: str, url: str):
        indexer = DocumentIndexer(url, id)
        indexer.index()

    def create_repository(
        self, repository_data: RepositoryCreate, background_tasks: BackgroundTasks
    ) -> Repository:
        """Create a new repository"""
        repository_id = str(uuid.uuid4())
        now = get_utc_now_naive()

        # TiDB compatible: Split INSERT and SELECT instead of using RETURNING
        insert_query = text("""
            INSERT INTO repository (id, name, url, document_url, created_at, updated_at)
            VALUES (:id, :name, :url, :document_url, :created_at, :updated_at)
        """)

        self.db.execute(
            insert_query,
            {
                "id": repository_id,
                "name": repository_data.name,
                "url": repository_data.url,
                "document_url": repository_data.document_url,
                "created_at": now,
                "updated_at": now,
            },
        )

        self.db.commit()

        # Fetch the inserted record
        select_query = text("""
            SELECT id, name, url, document_url, created_at, updated_at
            FROM repository
            WHERE id = :id
        """)
        
        result = self.db.execute(select_query, {"id": repository_id})
        row = result.fetchone()

        background_tasks.add_task(
            self._index_repository, repository_id, repository_data.url
        )

        background_tasks.add_task(
            self._index_documents, repository_id, repository_data.document_url
        )

        return Repository(
            id=row.id,
            name=row.name,
            url=row.url,
            document_url=row.document_url,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive(),
        )

    def get_repository(self, repository_id: str) -> Optional[Repository]:
        """Get a repository by ID"""
        query = text("""
            SELECT id, name, url, document_url, created_at, updated_at
            FROM repository
            WHERE id = :id
        """)

        result = self.db.execute(query, {"id": repository_id})
        row = result.fetchone()

        if not row:
            return None

        return Repository(
            id=row.id,
            name=row.name,
            url=row.url,
            document_url=row.document_url,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive(),
        )

    def get_repositories(
        self, skip: int = 0, limit: int = 100
    ) -> List[Repository]:
        """Get all repositories with pagination"""
        query = text("""
            SELECT id, name, url, document_url, created_at, updated_at
            FROM repository
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """)

        result = self.db.execute(query, {"skip": skip, "limit": limit})
        rows = result.fetchall()

        return [
            Repository(
                id=row.id,
                name=row.name,
                url=row.url,
                document_url=row.document_url,
                created_at=row.created_at or get_utc_now_naive(),
                updated_at=row.updated_at or get_utc_now_naive(),
            )
            for row in rows
        ]

    def update_repository(
        self, repository_id: str, update_data: RepositoryUpdate
    ) -> Optional[Repository]:
        """Update a repository"""
        # First check if repository exists
        existing = self.get_repository(repository_id)
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

        if update_data.document_url is not None:
            update_fields.append("document_url = :document_url")
            params["document_url"] = update_data.document_url

        if not update_fields:
            return existing  # No fields to update

        # TiDB compatible: Split UPDATE and SELECT instead of using RETURNING
        update_query = text(f"""
            UPDATE repository
            SET {", ".join(update_fields)}, updated_at = :updated_at
            WHERE id = :id
        """)

        self.db.execute(update_query, params)
        self.db.commit()

        # Fetch the updated record
        select_query = text("""
            SELECT id, name, url, document_url, created_at, updated_at
            FROM repository
            WHERE id = :id
        """)
        
        result = self.db.execute(select_query, {"id": repository_id})
        row = result.fetchone()

        return Repository(
            id=row.id,
            name=row.name,
            url=row.url,
            document_url=row.document_url,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive(),
        )

    def delete_repository(self, repository_id: str) -> bool:
        """Delete a repository"""
        # First check if repository exists
        existing = self.get_repository(repository_id)
        if not existing:
            return False

        query = text("DELETE FROM repository WHERE id = :id")
        self.db.execute(query, {"id": repository_id})
        self.db.commit()

        return True

    def get_repository_count(self) -> int:
        """Get total count of repositories"""
        query = text("SELECT COUNT(*) as count FROM repository")
        result = self.db.execute(query)
        return result.scalar() or 0

    def get_repository_crashes(
        self, repository_id: str, skip: int = 0, limit: int = 100
    ) -> List[Crash]:
        """Get all crashes for a specific repository with pagination"""
        query = text("""
            SELECT id, component, error_type, severity, status, impacted_users, 
                   comment, error_log, created_at, updated_at
            FROM crash
            WHERE repository_id = :repository_id
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """)

        result = self.db.execute(
            query, {"repository_id": repository_id, "skip": skip, "limit": limit}
        )
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
                updated_at=row.updated_at or get_utc_now_naive(),
            )
            for row in rows
        ]

    def get_repository_crash_count(self, repository_id: str) -> int:
        """Get total count of crashes for a specific repository"""
        query = text(
            "SELECT COUNT(*) as count FROM crash WHERE repository_id = :repository_id"
        )
        result = self.db.execute(query, {"repository_id": repository_id})
        return result.scalar() or 0

    def get_crash_rca(self, crash_id: str) -> Optional[CrashRCA]:
        """Get RCA document by crash ID"""
        query = text(
            """
            SELECT id, crash_id, description, problem_identification, data_collection,
                   root_cause_identification, solution, author, supporting_documents,
                   created_at, updated_at, git_diff, pull_request_url
            FROM crash_rca
            WHERE crash_id = :crash_id
            """
        )

        result = self.db.execute(query, {"crash_id": crash_id})
        row = result.fetchone()

        if not row:
            return None

        # Parse JSON fields if they are strings
        author = row.author
        if isinstance(author, str):
            try:
                author = json.loads(author)
            except (json.JSONDecodeError, TypeError):
                author = None

        supporting_documents = row.supporting_documents
        if isinstance(supporting_documents, str):
            try:
                supporting_documents = json.loads(supporting_documents)
            except (json.JSONDecodeError, TypeError):
                supporting_documents = None

        return CrashRCA(
            id=row.id,
            crash_id=row.crash_id,
            description=row.description,
            problem_identification=row.problem_identification,
            data_collection=row.data_collection,
            root_cause_identification=row.root_cause_identification,
            solution=row.solution,
            author=author,
            supporting_documents=supporting_documents,
            git_diff=row.git_diff,
            pull_request_url=row.pull_request_url,
            created_at=row.created_at or get_utc_now_naive(),
            updated_at=row.updated_at or get_utc_now_naive(),
        )

    def get_crash(self, crash_id: str) -> Optional[Crash]:
        """Get a crash by ID"""
        query = text("""
            SELECT id, component, error_type, severity, status, impacted_users, 
                   comment, error_log, repository_id, created_at, updated_at
            FROM crash
            WHERE id = :id
        """)

        result = self.db.execute(query, {"id": crash_id})
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
            updated_at=row.updated_at or get_utc_now_naive(),
        )

    def update_crash(
        self, crash_id: str, update_data: CrashUpdate
    ) -> Optional[Crash]:
        """Update a crash with new status and/or comment"""
        # First check if crash exists
        existing = self.get_crash(crash_id)
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

        # TiDB compatible: Split UPDATE and SELECT instead of using RETURNING
        update_query = text(f"""
            UPDATE crash
            SET {", ".join(update_fields)}, updated_at = :updated_at
            WHERE id = :id
        """)

        self.db.execute(update_query, params)
        self.db.commit()

        # Fetch the updated record
        select_query = text("""
            SELECT id, component, error_type, severity, status, impacted_users, 
                   comment, error_log, repository_id, created_at, updated_at
            FROM crash
            WHERE id = :id
        """)
        
        result = self.db.execute(select_query, {"id": crash_id})
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
            updated_at=row.updated_at or get_utc_now_naive(),
        )

    def get_crash_with_rca(self, crash_id: str) -> Optional[CrashWithRCA]:
        """Get crash data along with its RCA document by crash ID"""
        # First get the crash data
        crash = self.get_crash(crash_id)
        if not crash:
            return None
        
        # Then get the RCA data (optional)
        rca = self.get_crash_rca(crash_id)
        
        return CrashWithRCA(
            crash=crash,
            rca=rca
        )

    def update_crash_rca(
        self, crash_id: str, update_data: CrashRCAUpdate
    ) -> Optional[CrashRCA]:
        """Update RCA data for a crash"""
        # First check if RCA exists
        existing_rca = self.get_crash_rca(crash_id)
        if not existing_rca:
            return None

        # Build update query dynamically based on provided fields
        update_fields = []
        params = {"crash_id": crash_id, "updated_at": get_utc_now_naive()}

        if update_data.description is not None:
            update_fields.append("description = :description")
            params["description"] = update_data.description

        if update_data.problem_identification is not None:
            update_fields.append("problem_identification = :problem_identification")
            params["problem_identification"] = update_data.problem_identification

        if update_data.data_collection is not None:
            update_fields.append("data_collection = :data_collection")
            params["data_collection"] = update_data.data_collection

        if update_data.root_cause_identification is not None:
            update_fields.append("root_cause_identification = :root_cause_identification")
            params["root_cause_identification"] = update_data.root_cause_identification

        if update_data.solution is not None:
            update_fields.append("solution = :solution")
            params["solution"] = update_data.solution

        if update_data.author is not None:
            update_fields.append("author = :author")
            params["author"] = json.dumps(update_data.author) if update_data.author else None

        if update_data.supporting_documents is not None:
            update_fields.append("supporting_documents = :supporting_documents")
            params["supporting_documents"] = json.dumps(update_data.supporting_documents) if update_data.supporting_documents else None

        if update_data.git_diff is not None:
            update_fields.append("git_diff = :git_diff")
            params["git_diff"] = update_data.git_diff

        if update_data.pull_request_url is not None:
            update_fields.append("pull_request_url = :pull_request_url")
            params["pull_request_url"] = update_data.pull_request_url

        if not update_fields:
            return existing_rca  # No fields to update

        # TiDB compatible: Split UPDATE and SELECT instead of using RETURNING
        update_query = text(f"""
            UPDATE crash_rca
            SET {", ".join(update_fields)}, updated_at = :updated_at
            WHERE crash_id = :crash_id
        """)

        self.db.execute(update_query, params)
        self.db.commit()

        # Return the updated RCA
        return self.get_crash_rca(crash_id)

    def search_repositories(
        self, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[Repository]:
        """Search repositories by name or URL"""
        # TiDB compatible: Replace ILIKE with LIKE and UPPER() for case-insensitive search
        query = text("""
            SELECT id, name, url, document_url, created_at, updated_at
            FROM repository
            WHERE UPPER(name) LIKE UPPER(:search_term) OR UPPER(url) LIKE UPPER(:search_term)
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
        """)

        result = self.db.execute(
            query, {"search_term": f"%{search_term}%", "skip": skip, "limit": limit}
        )
        rows = result.fetchall()

        return [
            Repository(
                id=row.id,
                name=row.name,
                url=row.url,
                document_url=row.document_url,
                created_at=row.created_at or get_utc_now_naive(),
                updated_at=row.updated_at or get_utc_now_naive(),
            )
            for row in rows
        ]

from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


class Repository(Base):
    """Repository SQLAlchemy model"""

    __tablename__ = "repository"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    document_url = Column(String(500), nullable=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    crashes = relationship("Crash", back_populates="repository")


class Crash(Base):
    """Crash SQLAlchemy model"""

    __tablename__ = "crash"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    component = Column(String(255), nullable=False)
    error_type = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False)
    impacted_users = Column(Integer, nullable=False)
    comment = Column(String(500))
    repository_id = Column(String, ForeignKey("repository.id"), nullable=False)
    error_log = Column(String())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    repository = relationship("Repository", back_populates="crashes")
    rca = relationship("CrashRCA", back_populates="crash", uselist=False)


class CrashRCA(Base):
    """Crash RCA SQLAlchemy model"""

    __tablename__ = "crash_rca"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    crash_id = Column(String, ForeignKey("crash.id"), nullable=False)
    description = Column(Text)
    problem_identification = Column(Text)
    data_collection = Column(Text)
    root_cause_identification = Column(Text)
    solution = Column(Text)
    author = Column(JSON)
    supporting_documents = Column(JSON)
    git_diff = Column(String())
    pull_request_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationship
    crash = relationship("Crash", back_populates="rca")

import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Numeric, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.ext.associationproxy import association_proxy

class JobStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    budget = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SQLEnum(JobStatus, name="job_status_enum"),
        default=JobStatus.OPEN,
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    client = relationship("User", foreign_keys=[client_id], back_populates="jobs")
    job_skill_associations = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    skills = association_proxy("job_skill_associations", "skill")
    proposals = relationship("Proposal", back_populates="job", cascade="all, delete-orphan")
    contract = relationship("Contract", back_populates="job", uselist=False)
import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Numeric, Integer, DateTime, Enum as SQLEnum, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base


class MilestoneStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String(36), ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(
        SQLEnum(MilestoneStatus, name="milestone_status_enum"),
        default=MilestoneStatus.PENDING,
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

    contract = relationship("Contract", back_populates="milestones")
    # Missing relationship that caused the error:
    attachments = relationship("MilestoneAttachment", back_populates="milestone", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_milestone_amount_positive"),
    )


class MilestoneAttachment(Base):
    __tablename__ = "milestone_attachments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    milestone_id = Column(String(36), ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_url = Column(String(1000), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    milestone = relationship("Milestone", back_populates="attachments")
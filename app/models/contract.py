import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Numeric, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base


class ContractStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="RESTRICT"), unique=True, nullable=False)
    proposal_id = Column(String(36), ForeignKey("proposals.id", ondelete="RESTRICT"), unique=True, nullable=False)
    client_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    freelancer_id = Column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        SQLEnum(ContractStatus, name="contract_status_enum"),
        default=ContractStatus.ACTIVE,
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

    job = relationship("Job", back_populates="contract")
    proposal = relationship("Proposal", back_populates="contract")
    client = relationship("User", foreign_keys=[client_id], back_populates="client_contracts")
    freelancer = relationship("User", foreign_keys=[freelancer_id], back_populates="freelancer_contracts")
    milestones = relationship("Milestone", back_populates="contract", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="contract", cascade="all, delete-orphan")
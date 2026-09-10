import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Numeric, DateTime, Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base


class ProposalStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    freelancer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    cover_letter = Column(Text, nullable=False)
    bid_amount = Column(Numeric(10, 2), nullable=False)
    estimated_duration = Column(String(100), nullable=False)
    status = Column(
        SQLEnum(ProposalStatus, name="proposal_status_enum"),
        default=ProposalStatus.PENDING,
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

    job = relationship("Job", back_populates="proposals")
    freelancer = relationship("User", foreign_keys=[freelancer_id], back_populates="proposals")
    contract = relationship("Contract", back_populates="proposal", uselist=False)

    __table_args__ = (
        UniqueConstraint("job_id", "freelancer_id", name="uq_job_freelancer_proposal"),
    )
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Numeric, DateTime, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base
from sqlalchemy.ext.associationproxy import association_proxy


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    freelancer_associations = relationship("FreelancerSkill", back_populates="skill", cascade="all, delete-orphan")
    job_associations = relationship("JobSkill", back_populates="skill", cascade="all, delete-orphan")


class FreelancerProfile(Base):
    __tablename__ = "freelancer_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    experience = Column(Text, nullable=True)
    availability = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user = relationship("User", back_populates="freelancer_profile")
    skill_associations = relationship(
        "FreelancerSkill", 
        back_populates="profile", 
        cascade="all, delete-orphan"
    )
    skills = association_proxy("skill_associations", "skill")

class FreelancerSkill(Base):
    __tablename__ = "freelancer_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String(36), ForeignKey("freelancer_profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    profile = relationship("FreelancerProfile", back_populates="skill_associations")
    skill = relationship("Skill", back_populates="freelancer_associations")

    __table_args__ = (
        UniqueConstraint("profile_id", "skill_id", name="uq_freelancer_skill"),
    )
class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)

    job = relationship("Job", back_populates="job_skill_associations")
    skill = relationship("Skill", back_populates="job_associations")

    __table_args__ = (
        UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )
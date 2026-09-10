from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.job import JobStatus
from app.schemas.skill import SkillResponse


class JobBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    budget: Decimal = Field(..., gt=Decimal("0.00"))


class JobCreate(JobBase):
    skill_ids: list[int] = Field(default_factory=list)


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    description: str | None = Field(default=None, min_length=20)
    budget: Decimal | None = Field(default=None, gt=Decimal("0.00"))
    status: JobStatus | None = None
    skill_ids: list[int] | None = None


class JobFilterParams(BaseModel):
    search: str | None = None
    min_budget: Decimal | None = Field(default=None, ge=Decimal("0.00"))
    max_budget: Decimal | None = Field(default=None, ge=Decimal("0.00"))
    skill_ids: list[int] | None = None
    status: JobStatus | None = JobStatus.OPEN


class JobResponse(JobBase):
    id: str
    client_id: str
    status: JobStatus
    skills: list[SkillResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
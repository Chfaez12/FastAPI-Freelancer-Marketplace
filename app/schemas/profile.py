from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.skill import SkillResponse
from app.schemas.auth import UserResponse


class FreelancerProfileCreate(BaseModel):
    bio: str | None = None
    hourly_rate: Decimal | None = None
    experience: str | None = None
    availability: str | None = None
    skill_ids: list[int] = []

class FreelancerProfileUpdate(BaseModel):
    bio: str | None = None
    hourly_rate: Decimal | None = None
    experience: str | None = None
    availability: str | None = None
    skill_ids: list[int] | None = None

class FreelancerProfileResponse(BaseModel):
    id: str
    user_id: str
    bio: str | None = None
    hourly_rate: Decimal | None = None
    experience: str | None = None
    availability: str | None = None
    skills: list[SkillResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FreelancerDirectoryItem(BaseModel):
    id: str
    user_id: str
    user: UserResponse
    bio: str | None = None
    hourly_rate: Decimal | None = None
    experience: str | None = None
    availability: str | None = None
    skills: list[SkillResponse] = []

    model_config = ConfigDict(from_attributes=True)
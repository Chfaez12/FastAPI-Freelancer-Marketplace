from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SkillBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Updated skill name")

    
class SkillResponse(SkillBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
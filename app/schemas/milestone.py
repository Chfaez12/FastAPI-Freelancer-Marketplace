from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.milestone import MilestoneStatus


class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str | None = None
    amount: Decimal = Field(..., gt=Decimal("0.00"))
    deadline: datetime | None = None


class MilestoneCreate(MilestoneBase):
    pass


class MilestoneReviewAction(BaseModel):
    action: MilestoneStatus = Field(..., description="Must be either APPROVED or REJECTED")


class MilestoneResponse(MilestoneBase):
    id: str
    contract_id: str
    status: MilestoneStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MilestoneAttachmentResponse(BaseModel):
    id: str
    milestone_id: str
    file_name: str
    file_url: str
    file_size_bytes: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MilestoneResponse(MilestoneBase):
    id: str
    contract_id: str
    status: MilestoneStatus
    attachments: list[MilestoneAttachmentResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MilestoneUpdate(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    description: str | None = None
    amount: Decimal | None = Field(None, gt=0)
    deadline: datetime | None = None
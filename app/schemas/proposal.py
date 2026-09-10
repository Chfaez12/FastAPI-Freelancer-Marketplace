from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.proposal import ProposalStatus


class ProposalCreate(BaseModel):
    cover_letter: str = Field(..., min_length=20)
    bid_amount: Decimal = Field(..., gt=Decimal("0.00"))
    estimated_duration: str = Field(..., min_length=2, max_length=100)


class ProposalUpdate(BaseModel):
    cover_letter: str | None = Field(default=None, min_length=20)
    bid_amount: Decimal | None = Field(default=None, gt=Decimal("0.00"))
    estimated_duration: str | None = Field(default=None, min_length=2, max_length=100)


class ProposalResponse(BaseModel):
    id: str
    job_id: str
    freelancer_id: str
    cover_letter: str
    bid_amount: Decimal
    estimated_duration: str
    status: ProposalStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProposalUpdate(BaseModel):
    cover_letter: str | None = Field(None, min_length=10, max_length=5000)
    bid_amount: Decimal | None = Field(None, gt=0)
    estimated_days: int | None = Field(None, gt=0)
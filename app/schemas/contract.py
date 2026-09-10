from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.models.contract import ContractStatus
from app.schemas.milestone import MilestoneResponse


class ContractResponse(BaseModel):
    id: str
    job_id: str
    proposal_id: str
    client_id: str
    freelancer_id: str
    total_amount: Decimal
    status: ContractStatus
    milestones: list[MilestoneResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
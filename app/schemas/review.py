from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating between 1 and 5")
    comment: str | None = Field(default=None, max_length=2000)

class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5, description="Updated rating from 1 to 5")
    comment: str | None = Field(None, min_length=5, max_length=2000, description="Updated review text")

    
class ReviewResponse(BaseModel):
    id: str
    contract_id: str
    reviewer_id: str
    reviewee_id: str
    rating: int
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
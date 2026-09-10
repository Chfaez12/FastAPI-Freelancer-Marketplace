from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user, get_db
from app.models.user import User
from app.repositories import review_repo
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.services import review_service

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post(
    "/contracts/{contract_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review for a completed contract",
)
def create_review(
    contract_id: str,
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return review_service.create_review(db, current_user, contract_id, data)


@router.get(
    "/contracts/{contract_id}",
    response_model=list[ReviewResponse],
    summary="List all reviews submitted for a specific contract",
)
def get_contract_reviews(contract_id: str, db: Session = Depends(get_db)):
    return review_service.list_contract_reviews(db, contract_id)


@router.get(
    "/users/{user_id}",
    response_model=list[ReviewResponse],
    summary="List all reviews received by a specific user (Freelancer or Client)",
)
def get_user_reviews(user_id: str, db: Session = Depends(get_db)):
    return review_repo.list_by_reviewee(db, user_id)

@router.patch(
    "/{review_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing review (Author only)",
)
def update_review_endpoint(
    review_id: str,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return review_service.update_review(db, current_user, review_id, data)
from sqlalchemy.orm import Session
from app.exceptions.custom_exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    InvalidWorkflowStateException,
)
from app.models.contract import ContractStatus
from app.models.review import Review
from app.models.user import User
from app.repositories import contract_repo, review_repo
from app.schemas.review import ReviewCreate, ReviewUpdate


def create_review(
    db: Session, current_user: User, contract_id: str, data: ReviewCreate
) -> Review:
    contract = contract_repo.get_by_id(db, contract_id)
    if not contract:
        raise ResourceNotFoundException("Contract", contract_id)

    if contract.status != ContractStatus.COMPLETED:
        raise InvalidWorkflowStateException("Reviews can only be submitted for COMPLETED contracts.")

    if current_user.id == contract.client_id:
        reviewer_id = contract.client_id
        reviewee_id = contract.freelancer_id
    elif current_user.id == contract.freelancer_id:
        reviewer_id = contract.freelancer_id
        reviewee_id = contract.client_id
    else:
        raise PermissionDeniedException("Only participants of this contract can leave a review.")

    existing_review = review_repo.get_by_contract_and_reviewer(db, contract_id, reviewer_id)
    if existing_review:
        raise ResourceAlreadyExistsException(
            "Review", "reviewer_id", "You have already reviewed this contract."
        )

    review = Review(
        contract_id=contract_id,
        reviewer_id=reviewer_id,
        reviewee_id=reviewee_id,
        rating=data.rating,
        comment=data.comment,
    )
    return review_repo.create(db, review)


def list_contract_reviews(db: Session, contract_id: str) -> list[Review]:
    return review_repo.list_by_contract(db, contract_id)

def update_review(
    db: Session,
    current_user: User,
    review_id: str,
    data: ReviewUpdate,
) -> Review:
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise ResourceNotFoundException("Review", review_id)

    if review.reviewer_id != current_user.id:
        raise PermissionDeniedException("You can only modify reviews you authored.")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review
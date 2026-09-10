from sqlalchemy.orm import Session
from app.models.review import Review
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self):
        super().__init__(Review)

    def get_by_contract_and_reviewer(
        self, db: Session, contract_id: str, reviewer_id: str
    ) -> Review | None:
        return (
            db.query(Review)
            .filter(
                Review.contract_id == contract_id,
                Review.reviewer_id == reviewer_id,
            )
            .first()
        )

    def list_by_contract(self, db: Session, contract_id: str) -> list[Review]:
        return db.query(Review).filter(Review.contract_id == contract_id).all()

    def list_by_reviewee(self, db: Session, user_id: str) -> list[Review]:
        return db.query(Review).filter(Review.reviewee_id == user_id).all()


review_repo = ReviewRepository()
from sqlalchemy.orm import Session, joinedload
from app.models.milestone import Milestone
from app.repositories.base import BaseRepository


class MilestoneRepository(BaseRepository[Milestone]):
    def __init__(self):
        super().__init__(Milestone)

    def get_by_id_with_attachments(self, db: Session, milestone_id: str) -> Milestone | None:
        return (
            db.query(Milestone)
            .options(joinedload(Milestone.attachments))
            .filter(Milestone.id == milestone_id)
            .first()
        )

    def list_by_contract(self, db: Session, contract_id: str) -> list[Milestone]:
        return (
            db.query(Milestone)
            .options(joinedload(Milestone.attachments))
            .filter(Milestone.contract_id == contract_id)
            .order_by(Milestone.created_at.asc())
            .all()
        )


milestone_repo = MilestoneRepository()
from sqlalchemy.orm import Session, joinedload
from app.models.contract import Contract
from app.models.milestone import Milestone
from app.repositories.base import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    def __init__(self):
        super().__init__(Contract)

    def get_detailed(self, db: Session, contract_id: str) -> Contract | None:
        return (
            db.query(Contract)
            .options(joinedload(Contract.milestones))
            .filter(Contract.id == contract_id)
            .first()
        )

    def list_by_user(self, db: Session, user_id: str) -> list[Contract]:
        return (
            db.query(Contract)
            .filter((Contract.client_id == user_id) | (Contract.freelancer_id == user_id))
            .order_by(Contract.created_at.desc())
            .all()
        )


class MilestoneRepository(BaseRepository[Milestone]):
    def __init__(self):
        super().__init__(Milestone)

    def list_by_contract(self, db: Session, contract_id: str) -> list[Milestone]:
        return (
            db.query(Milestone)
            .filter(Milestone.contract_id == contract_id)
            .order_by(Milestone.created_at.asc())
            .all()
        )


contract_repo = ContractRepository()
milestone_repo = MilestoneRepository()
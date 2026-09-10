from sqlalchemy.orm import Session
from app.models.proposal import Proposal, ProposalStatus
from app.repositories.base import BaseRepository


class ProposalRepository(BaseRepository[Proposal]):
    def __init__(self):
        super().__init__(Proposal)

    def get_by_job_and_freelancer(
        self, db: Session, job_id: str, freelancer_id: str
    ) -> Proposal | None:
        return (
            db.query(Proposal)
            .filter(Proposal.job_id == job_id, Proposal.freelancer_id == freelancer_id)
            .first()
        )

    def list_by_job(self, db: Session, job_id: str) -> list[Proposal]:
        return db.query(Proposal).filter(Proposal.job_id == job_id).all()

    def list_by_freelancer(self, db: Session, freelancer_id: str) -> list[Proposal]:
        return db.query(Proposal).filter(Proposal.freelancer_id == freelancer_id).all()

    def reject_all_other_pending(
        self, db: Session, job_id: str, accepted_proposal_id: str
    ) -> None:
        db.query(Proposal).filter(
            Proposal.job_id == job_id,
            Proposal.id != accepted_proposal_id,
            Proposal.status == ProposalStatus.PENDING,
        ).update(
            {"status": ProposalStatus.REJECTED},
            synchronize_session=False,
        )


proposal_repo = ProposalRepository()
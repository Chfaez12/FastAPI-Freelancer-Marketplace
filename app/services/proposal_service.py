from sqlalchemy.orm import Session
from app.exceptions.custom_exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    InvalidWorkflowStateException,
)
from app.models.contract import Contract, ContractStatus
from app.models.job import JobStatus
from app.models.proposal import Proposal, ProposalStatus
from app.models.user import User, UserRole
from app.repositories import job_repo, proposal_repo, contract_repo
from app.schemas.proposal import ProposalCreate, ProposalUpdate


def submit_proposal(
    db: Session, current_user: User, job_id: str, data: ProposalCreate
) -> Proposal:
    if current_user.role != UserRole.FREELANCER:
        raise PermissionDeniedException("Only freelancers can submit proposals.")

    job = job_repo.get_by_id(db, job_id)
    if not job:
        raise ResourceNotFoundException("Job", job_id)

    if job.status != JobStatus.OPEN:
        raise InvalidWorkflowStateException("Proposals can only be submitted to OPEN jobs.")

    if job.client_id == current_user.id:
        raise PermissionDeniedException("Cannot submit a proposal to your own job posting.")

    existing_proposal = proposal_repo.get_by_job_and_freelancer(db, job_id, current_user.id)
    if existing_proposal:
        raise ResourceAlreadyExistsException(
            "Proposal", "freelancer_id", f"Already applied to job {job_id}"
        )

    proposal = Proposal(
        job_id=job_id,
        freelancer_id=current_user.id,
        cover_letter=data.cover_letter,
        bid_amount=data.bid_amount,
        estimated_duration=data.estimated_duration,
        status=ProposalStatus.PENDING,
    )
    return proposal_repo.create(db, proposal)


def list_job_proposals(db: Session, current_user: User, job_id: str) -> list[Proposal]:
    job = job_repo.get_by_id(db, job_id)
    if not job:
        raise ResourceNotFoundException("Job", job_id)

    if job.client_id != current_user.id:
        raise PermissionDeniedException("Only the job owner can review all proposals.")

    return proposal_repo.list_by_job(db, job_id)


def accept_proposal(db: Session, current_user: User, proposal_id: str) -> Contract:
    
    proposal = proposal_repo.get_by_id(db, proposal_id)
    if not proposal:
        raise ResourceNotFoundException("Proposal", proposal_id)

    job = job_repo.get_for_update(db, proposal.job_id)
    if not job:
        raise ResourceNotFoundException("Job", proposal.job_id)

    if job.client_id != current_user.id:
        raise PermissionDeniedException("Only the job poster can accept proposals.")

    if job.status != JobStatus.OPEN:
        raise InvalidWorkflowStateException(
            f"Cannot accept proposal for a job that is {job.status.value}."
        )

    if proposal.status != ProposalStatus.PENDING:
        raise InvalidWorkflowStateException(
            f"Cannot accept proposal with status '{proposal.status.value}'."
        )

    proposal.status = ProposalStatus.ACCEPTED
    proposal_repo.reject_all_other_pending(db, job.id, proposal.id)

    job.status = JobStatus.IN_PROGRESS

    contract = Contract(
        job_id=job.id,
        proposal_id=proposal.id,
        client_id=job.client_id,
        freelancer_id=proposal.freelancer_id,
        total_amount=proposal.bid_amount,
        status=ContractStatus.ACTIVE,
    )
    contract = contract_repo.create(db, contract, commit=False)

    db.commit()
    return contract_repo.get_detailed(db, contract.id)


def delete_proposal(db: Session, current_user: User, proposal_id: str) -> None:
    proposal = proposal_repo.get_by_id(db, proposal_id)
    if not proposal:
        raise ResourceNotFoundException("Proposal", proposal_id)

    if proposal.freelancer_id != current_user.id:
        raise PermissionDeniedException("Only the freelancer who submitted this proposal can withdraw it.")

    if proposal.status != ProposalStatus.PENDING:
        raise InvalidWorkflowStateException(
            f"Cannot delete or withdraw proposal with status '{proposal.status.value}'. Only PENDING proposals can be deleted."
        )

    proposal_repo.delete(db, proposal)

def update_proposal(
    db: Session, current_user: User, proposal_id: str, data: ProposalUpdate
) -> Proposal:
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise ResourceNotFoundException("Proposal", proposal_id)

    if proposal.freelancer_id != current_user.id:
        raise PermissionDeniedException("You can only edit your own proposals.")

    if proposal.status != ProposalStatus.PENDING:
        raise InvalidWorkflowStateException(
            f"Cannot update proposal in '{proposal.status}' status. Only PENDING proposals can be edited."
        )

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(proposal, field, value)

    db.commit()
    db.refresh(proposal)
    return proposal
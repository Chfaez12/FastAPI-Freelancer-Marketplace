from sqlalchemy.orm import Session
from app.exceptions.custom_exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
    InvalidWorkflowStateException,
)
from app.models.contract import Contract, ContractStatus
from app.models.job import JobStatus
from app.models.milestone import Milestone, MilestoneStatus
from app.models.user import User
from app.repositories import contract_repo, milestone_repo, job_repo
from app.schemas.milestone import MilestoneCreate, MilestoneReviewAction


def get_contract(db: Session, current_user: User, contract_id: str) -> Contract:
    contract = contract_repo.get_detailed(db, contract_id)
    if not contract:
        raise ResourceNotFoundException("Contract", contract_id)

    if current_user.id not in (contract.client_id, contract.freelancer_id):
        raise PermissionDeniedException("You are not an authorized participant in this contract.")

    return contract


def list_user_contracts(db: Session, current_user: User) -> list[Contract]:
    return contract_repo.list_by_user(db, current_user.id)


def add_milestone(
    db: Session, current_user: User, contract_id: str, data: MilestoneCreate
) -> Milestone:
    contract = contract_repo.get_by_id(db, contract_id)
    if not contract:
        raise ResourceNotFoundException("Contract", contract_id)

    if contract.client_id != current_user.id:
        raise PermissionDeniedException("Only the client can add milestones.")

    if contract.status != ContractStatus.ACTIVE:
        raise InvalidWorkflowStateException("Milestones cannot be added to non-active contracts.")

    milestone = Milestone(
        contract_id=contract_id,
        title=data.title,
        description=data.description,
        amount=data.amount,
        deadline=data.deadline,
        status=MilestoneStatus.PENDING,
    )
    return milestone_repo.create(db, milestone)


def submit_milestone(db: Session, current_user: User, milestone_id: str) -> Milestone:
    milestone = milestone_repo.get_by_id(db, milestone_id)
    if not milestone:
        raise ResourceNotFoundException("Milestone", milestone_id)

    contract = contract_repo.get_by_id(db, milestone.contract_id)
    if contract.freelancer_id != current_user.id:
        raise PermissionDeniedException("Only the assigned freelancer can submit this milestone.")

    if milestone.status not in (MilestoneStatus.PENDING, MilestoneStatus.REJECTED):
        raise InvalidWorkflowStateException(
            f"Cannot submit milestone from status '{milestone.status.value}'."
        )

    milestone.status = MilestoneStatus.SUBMITTED
    db.commit()
    db.refresh(milestone)
    return milestone_repo.get_by_id(db, milestone_id)


def review_milestone(
    db: Session, current_user: User, milestone_id: str, action: MilestoneReviewAction
) -> Milestone:
    milestone = milestone_repo.get_by_id(db, milestone_id)
    if not milestone:
        raise ResourceNotFoundException("Milestone", milestone_id)

    contract = contract_repo.get_by_id(db, milestone.contract_id)
    if contract.client_id != current_user.id:
        raise PermissionDeniedException("Only the client can approve or reject milestones.")

    if milestone.status != MilestoneStatus.SUBMITTED:
        raise InvalidWorkflowStateException("Can only review milestones in 'SUBMITTED' state.")

    if action.action not in (MilestoneStatus.APPROVED, MilestoneStatus.REJECTED):
        raise InvalidWorkflowStateException("Action must be either APPROVED or REJECTED.")

    milestone.status = action.action
    db.commit()
    db.refresh(milestone)
    return milestone_repo.get_by_id(db, milestone_id)


def complete_contract(db: Session, current_user: User, contract_id: str) -> Contract:
    contract = contract_repo.get_detailed(db, contract_id)
    if not contract:
        raise ResourceNotFoundException("Contract", contract_id)

    if contract.client_id != current_user.id:
        raise PermissionDeniedException("Only the client can mark the contract as complete.")

    if contract.status != ContractStatus.ACTIVE:
        raise InvalidWorkflowStateException("Contract is not currently active.")

    if not contract.milestones:
        raise InvalidWorkflowStateException("Cannot complete contract without any milestones.")

    has_incomplete = any(m.status != MilestoneStatus.APPROVED for m in contract.milestones)
    if has_incomplete:
        raise InvalidWorkflowStateException(
            "All milestones must be APPROVED before completing the contract."
        )

    contract.status = ContractStatus.COMPLETED

    job = job_repo.get_by_id(db, contract.job_id)
    if job:
        job.status = JobStatus.COMPLETED

    db.commit()
    return contract_repo.get_detailed(db, contract_id)


def delete_milestone(db: Session, current_user: User, milestone_id: str) -> None:
    milestone = milestone_repo.get_by_id(db, milestone_id)
    if not milestone:
        raise ResourceNotFoundException("Milestone", milestone_id)

    contract = contract_repo.get_by_id(db, milestone.contract_id)
    if not contract:
        raise ResourceNotFoundException("Contract", milestone.contract_id)

    if contract.client_id != current_user.id:
        raise PermissionDeniedException("Only the client can delete milestones from this contract.")

    if contract.status != ContractStatus.ACTIVE:
        raise InvalidWorkflowStateException("Milestones can only be removed from an ACTIVE contract.")

    if milestone.status != MilestoneStatus.PENDING:
        raise InvalidWorkflowStateException(
            f"Cannot delete a milestone in '{milestone.status.value}' state. Only PENDING milestones can be deleted."
        )

    milestone_repo.delete(db, milestone)
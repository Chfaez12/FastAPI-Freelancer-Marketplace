from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.contract import ContractResponse
from app.schemas.milestone import MilestoneCreate, MilestoneResponse
from app.services import contract_service

router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get(
    "",
    response_model=list[ContractResponse],
    summary="List all contracts for current user (Client or Freelancer)",
)
def list_my_contracts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return contract_service.list_user_contracts(db, current_user)


@router.get(
    "/{contract_id}",
    response_model=ContractResponse,
    summary="Get contract details by ID",
)
def get_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return contract_service.get_contract(db, current_user, contract_id)


@router.post(
    "/{contract_id}/milestones",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a milestone to an active contract (Client only)",
)
def add_milestone(
    contract_id: str,
    data: MilestoneCreate,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    return contract_service.add_milestone(db, current_user, contract_id, data)


@router.post(
    "/{contract_id}/complete",
    response_model=ContractResponse,
    summary="Mark contract as completed (Client only, all milestones must be approved)",
)
def complete_contract(
    contract_id: str,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    return contract_service.complete_contract(db, current_user, contract_id)
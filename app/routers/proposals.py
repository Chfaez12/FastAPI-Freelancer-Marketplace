from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.contract import ContractResponse
from app.schemas.proposal import ProposalResponse, ProposalUpdate
from app.services import proposal_service
from app.repositories import proposal_repo
from app.exceptions.custom_exceptions import ResourceNotFoundException, PermissionDeniedException

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.get(
    "",
    response_model=list[ProposalResponse],
    summary="List proposals submitted by logged-in freelancer",
)
def get_my_proposals(
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    return proposal_repo.list_by_freelancer(db, current_user.id)


@router.get(
    "/{proposal_id}",
    response_model=ProposalResponse,
    summary="Get single proposal details",
)
def get_proposal(
    proposal_id: str,
    current_user: User = Depends(require_roles(UserRole.CLIENT, UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    proposal = proposal_repo.get_by_id(db, proposal_id)
    if not proposal:
        raise ResourceNotFoundException("Proposal", proposal_id)
    
    if current_user.id != proposal.freelancer_id and current_user.id != proposal.job.client_id:
        raise PermissionDeniedException("You are not authorized to view this proposal.")
        
    return proposal


@router.post(
    "/{proposal_id}/accept",
    response_model=ContractResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Accept proposal and initiate active contract (Client owner only)",
)
def accept_proposal(
    proposal_id: str,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    return proposal_service.accept_proposal(db, current_user, proposal_id)

@router.delete(
    "/{proposal_id}",
    status_code=status.HTTP_200_OK,
    summary="Withdraw/delete proposal (Freelancer owner only, PENDING only)",
)
def delete_proposal(
    proposal_id: str,
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    proposal_service.delete_proposal(db, current_user, proposal_id)
    return {"message": "Proposal withdrawn and deleted successfully", "proposal_id": proposal_id}


@router.patch(
    "/{proposal_id}",
    response_model=ProposalResponse,
    summary="Update proposal details (Freelancer owner only, PENDING only)",
)
def patch_proposal(
    proposal_id: str,
    data: ProposalUpdate,
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    return proposal_service.update_proposal(db, current_user, proposal_id, data)
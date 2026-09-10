from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth import get_db, require_roles
from app.exceptions.custom_exceptions import InvalidWorkflowStateException, PermissionDeniedException, ResourceNotFoundException
from app.models.user import User, UserRole
from app.repositories import contract_repository
from app.schemas.milestone import MilestoneAttachmentResponse, MilestoneResponse, MilestoneReviewAction
from app.services import contract_service
from fastapi import File, UploadFile
from app.models.milestone import MilestoneAttachment, MilestoneStatus
from app.services.storage_service import upload_file_to_supabase, ALLOWED_DOCUMENT_TYPES
from app.repositories import milestone_repo, contract_repo
from app.models.contract import Contract
from app.schemas.milestone import MilestoneUpdate, MilestoneResponse
from app.models.milestone import Milestone, MilestoneStatus

router = APIRouter(prefix="/milestones", tags=["Milestones"])


@router.post(
    "/{milestone_id}/submit",
    response_model=MilestoneResponse,
    summary="Submit milestone for review (Assigned Freelancer only)",
)
def submit_milestone(
    milestone_id: str,
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    return contract_service.submit_milestone(db, current_user, milestone_id)


@router.post(
    "/{milestone_id}/review",
    response_model=MilestoneResponse,
    summary="Approve or Reject submitted milestone (Contract Client only)",
)
def review_milestone(
    milestone_id: str,
    action: MilestoneReviewAction,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    return contract_service.review_milestone(db, current_user, milestone_id, action)

from fastapi import status

@router.delete(
    "/{milestone_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a pending milestone (Contract Client only)",
)
def delete_milestone(
    milestone_id: str,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    contract_service.delete_milestone(db, current_user, milestone_id)
    return {"message": "Milestone removed successfully", "milestone_id": milestone_id}

@router.post(
    "/{milestone_id}/attachments",
    response_model=MilestoneAttachmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Attach deliverable file to a milestone (Assigned freelancer only)",
)
def upload_milestone_attachment(
    milestone_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    milestone = milestone_repo.get_by_id(db, milestone_id)
    if not milestone:
        raise ResourceNotFoundException("Milestone", milestone_id)

    contract = contract_repo.get_by_id(db, milestone.contract_id)
    if contract.freelancer_id != current_user.id:
        raise PermissionDeniedException("Only the assigned freelancer can upload work to this milestone.")

    if milestone.status == MilestoneStatus.APPROVED:
        raise InvalidWorkflowStateException("Cannot add attachments to an already approved milestone.")

    upload_meta = upload_file_to_supabase(
        file=file,
        bucket="milestone-deliverables",
        path_prefix=f"contracts/{contract.id}/milestones/{milestone_id}",
        allowed_types=ALLOWED_DOCUMENT_TYPES,
    )

    attachment = MilestoneAttachment(
        milestone_id=milestone.id,
        file_name=upload_meta["file_name"],
        file_url=upload_meta["file_url"],
        file_size_bytes=upload_meta["file_size"],
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment

@router.patch(
    "/{milestone_id}",
    response_model=MilestoneResponse,
    summary="Update milestone details (Contract client owner only, PENDING only)",
)
def update_milestone(
    milestone_id: str,
    data: MilestoneUpdate,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise ResourceNotFoundException("Milestone", milestone_id)

    contract = db.query(Contract).filter(Contract.id == milestone.contract_id).first()
    if contract.client_id != current_user.id:
        raise PermissionDeniedException("Only the client who owns this contract can modify milestones.")

    if milestone.status in {MilestoneStatus.APPROVED, MilestoneStatus.SUBMITTED}:
        raise InvalidWorkflowStateException(
            f"Cannot edit milestone in '{milestone.status}' state."
        )

    update_dict = data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(milestone, field, value)

    db.commit()
    db.refresh(milestone)
    return milestone
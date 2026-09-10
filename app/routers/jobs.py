import math
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user, get_db, require_roles
from app.models.job import JobStatus
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.job import JobCreate, JobFilterParams, JobResponse, JobUpdate
from app.schemas.proposal import ProposalCreate, ProposalResponse
from app.services import job_service, proposal_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Post a new job (Clients only)",
)
def create_job(
    data: JobCreate,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    return job_service.create_job(db, current_user, data)


@router.get(
    "",
    response_model=PaginatedResponse[JobResponse],
    summary="Search and discover available jobs",
)
def list_jobs(
    search: str | None = None,
    min_budget: Decimal | None = None,
    max_budget: Decimal | None = None,
    skill_ids: list[int] = Query(default=None),
    status_filter: JobStatus | None = JobStatus.OPEN,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    filters = JobFilterParams(
        search=search,
        min_budget=min_budget,
        max_budget=max_budget,
        skill_ids=skill_ids,
        status=status_filter,
    )
    pagination = PaginationParams(page=page, limit=limit)
    items, total = job_service.list_jobs(db, filters, pagination)
    total_pages = math.ceil(total / limit) if total > 0 else 0

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get single job details",
)
def get_job(job_id: str, db: Session = Depends(get_db)):
    return job_service.get_job_details(db, job_id)


@router.patch(
    "/{job_id}",
    response_model=JobResponse,
    summary="Update job posting (Client owner only)",
)
def update_job(
    job_id: str,
    data: JobUpdate,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    return job_service.update_job(db, current_user, job_id, data)


@router.post(
    "/{job_id}/proposals",
    response_model=ProposalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit proposal for job (Freelancers only)",
)
def submit_proposal(
    job_id: str,
    data: ProposalCreate,
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    return proposal_service.submit_proposal(db, current_user, job_id, data)


@router.get(
    "/{job_id}/proposals",
    response_model=list[ProposalResponse],
    summary="List all proposals for job (Job owner client only)",
)
def list_job_proposals(
    job_id: str,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    return proposal_service.list_job_proposals(db, current_user, job_id)

@router.delete(
    "/{job_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a job posting (Owner Client only, DRAFT or OPEN only)",
)
def delete_job(
    job_id: str,
    current_user: User = Depends(require_roles(UserRole.CLIENT)),
    db: Session = Depends(get_db),
):
    job_service.delete_job(db, current_user, job_id)
    return {"message": "Job deleted successfully", "job_id": job_id}
from sqlalchemy.orm import Session
from app.exceptions.custom_exceptions import (
    PermissionDeniedException,
    ResourceNotFoundException,
    InvalidWorkflowStateException,
)
from app.models.job import Job, JobStatus
from app.models.user import User, UserRole
from app.repositories import job_repo
from app.schemas.common import PaginationParams
from app.schemas.job import JobCreate, JobFilterParams, JobUpdate

def create_job(db: Session, current_user: User, data: JobCreate) -> Job:
    if current_user.role != UserRole.CLIENT:
        raise PermissionDeniedException("Only clients can post jobs.")

    job = Job(
        client_id=current_user.id,
        title=data.title,
        description=data.description,
        budget=data.budget,
        status=JobStatus.OPEN,
    )
    job = job_repo.create(db, job, commit=False)
    db.flush()  

    if data.skill_ids:
        job_repo.set_skills(db, job.id, data.skill_ids)

    db.commit()
    return job_repo.get_detailed(db, job.id)

def list_jobs(
    db: Session, filters: JobFilterParams, pagination: PaginationParams
) -> tuple[list[Job], int]:
    skip = (pagination.page - 1) * pagination.limit
    return job_repo.list_filtered(db, filters, skip=skip, limit=pagination.limit)


def get_job_details(db: Session, job_id: str) -> Job:
    job = job_repo.get_detailed(db, job_id)
    if not job:
        raise ResourceNotFoundException("Job", job_id)
    return job


def update_job(db: Session, current_user: User, job_id: str, data: JobUpdate) -> Job:
    job = job_repo.get_detailed(db, job_id)
    if not job:
        raise ResourceNotFoundException("Job", job_id)

    if job.client_id != current_user.id:
        raise PermissionDeniedException("You are not authorized to update this job.")

    if job.status not in (JobStatus.DRAFT, JobStatus.OPEN):
        raise InvalidWorkflowStateException(
            f"Cannot modify a job in '{job.status.value}' status."
        )

    update_dict = data.model_dump(exclude_unset=True)
    skill_ids = update_dict.pop("skill_ids", None)

    for field, val in update_dict.items():
        setattr(job, field, val)

    if skill_ids is not None:
        job_repo.set_skills(db, job.id, skill_ids)

    db.commit()
    return job_repo.get_detailed(db, job.id)


def delete_job(db: Session, current_user: User, job_id: str) -> None:
    job = job_repo.get_by_id(db, job_id)
    if not job:
        raise ResourceNotFoundException("Job", job_id)

    if job.client_id != current_user.id:
        raise PermissionDeniedException("Only the job poster can delete this job.")

    if job.status not in (JobStatus.DRAFT, JobStatus.OPEN):
        raise InvalidWorkflowStateException(
            f"Cannot delete a job with status '{job.status.value}'. Only DRAFT or OPEN jobs can be deleted."
        )
    
    if job.contract:
        raise InvalidWorkflowStateException("Cannot delete a job that has an associated contract.")

    job_repo.delete(db, job)
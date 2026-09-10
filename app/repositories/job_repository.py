from sqlalchemy import distinct
from sqlalchemy.orm import Session, joinedload
from app.models.job import Job, JobStatus
from app.models.profile import JobSkill
from app.repositories.base import BaseRepository
from app.schemas.job import JobFilterParams


class JobRepository(BaseRepository[Job]):
    def __init__(self):
        super().__init__(Job)

    def get_detailed(self, db: Session, job_id: str) -> Job | None:
        return (
            db.query(Job)
            .options(joinedload(Job.job_skill_associations).joinedload(JobSkill.skill))
            .filter(Job.id == job_id)
            .first()
        )

    def get_for_update(self, db: Session, job_id: str) -> Job | None:
        """Pessimistic lock to prevent concurrent proposal acceptance."""
        return db.query(Job).filter(Job.id == job_id).with_for_update().first()

    def list_filtered(
        self, db: Session, filters: JobFilterParams, skip: int = 0, limit: int = 20
    ) -> tuple[list[Job], int]:
        query = db.query(Job).options(joinedload(Job.job_skill_associations).joinedload(JobSkill.skill))

        if filters.status:
            query = query.filter(Job.status == filters.status)

        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.filter(
                (Job.title.ilike(pattern)) | (Job.description.ilike(pattern))
            )

        if filters.min_budget is not None:
            query = query.filter(Job.budget >= filters.min_budget)

        if filters.max_budget is not None:
            query = query.filter(Job.budget <= filters.max_budget)

        if filters.skill_ids:
            query = query.join(Job.skills).filter(JobSkill.skill_id.in_(filters.skill_ids))

        total = query.with_entities(distinct(Job.id)).count()
        jobs = query.order_by(Job.created_at.desc()).offset(skip).limit(limit).all()

        return jobs, total

    def set_skills(self, db: Session, job_id: str, skill_ids: list[int]) -> None:
        db.query(JobSkill).filter(JobSkill.job_id == job_id).delete()
        for skill_id in set(skill_ids):
            db.add(JobSkill(job_id=job_id, skill_id=skill_id))
        db.flush()


job_repo = JobRepository()
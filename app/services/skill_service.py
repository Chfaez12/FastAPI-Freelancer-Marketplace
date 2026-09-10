from sqlalchemy.orm import Session
from app.models.profile import Skill, FreelancerSkill, JobSkill
from app.schemas.skill import SkillUpdate
from app.repositories.skill_repository import skill_repo
from app.exceptions.custom_exceptions import (
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
    InvalidWorkflowStateException,
)


def update_skill(db: Session, skill_id: int, data: SkillUpdate) -> Skill:
    skill = skill_repo.get_by_id(db, skill_id)
    if not skill:
        raise ResourceNotFoundException("Skill", skill_id)

    normalized_name = data.name.strip()
    duplicate = skill_repo.get_by_name_excluding_id(db, normalized_name, skill_id)
    if duplicate:
        raise ResourceAlreadyExistsException("Skill", "name", normalized_name)

    skill.name = normalized_name
    db.commit()
    db.refresh(skill)
    return skill


def delete_skill(db: Session, skill_id: int) -> None:
    skill = skill_repo.get_by_id(db, skill_id)
    if not skill:
        raise ResourceNotFoundException("Skill", skill_id)

    has_freelancer_links = (
        db.query(FreelancerSkill).filter(FreelancerSkill.skill_id == skill_id).first()
    )
    if has_freelancer_links:
        raise InvalidWorkflowStateException(
            f"Cannot delete skill '{skill.name}'. It is linked to one or more freelancer profiles."
        )
    has_job_links = (
        db.query(JobSkill).filter(JobSkill.skill_id == skill_id).first()
    )
    if has_job_links:
        raise InvalidWorkflowStateException(
            f"Cannot delete skill '{skill.name}'. It is attached to one or more job listings."
        )

    skill_repo.delete(db, skill)
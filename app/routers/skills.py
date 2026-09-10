from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user, get_db
from app.models.profile import Skill
from app.models.user import User
from app.repositories import skill_repo
from app.schemas.skill import SkillCreate, SkillResponse
from app.services import skill_service
from app.schemas.skill import SkillResponse, SkillUpdate

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("", response_model=list[SkillResponse], summary="List all available skills")
def list_skills(db: Session = Depends(get_db)):
    return skill_repo.get_all(db)


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new skill",
)
def create_skill(
    data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = skill_repo.get_by_name(db, data.name)
    if existing:
        return existing
    skill = Skill(name=data.name.strip())
    return skill_repo.create(db, skill)


@router.patch(
    "/{skill_id}",
    response_model=SkillResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing skill",
)
def update_skill(
    skill_id: int,
    data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return skill_service.update_skill(db, skill_id, data)


@router.delete(
    "/{skill_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a skill (Allowed only if unlinked)",
)
def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill_service.delete_skill(db, skill_id)
    return {"message": "Skill deleted successfully", "skill_id": skill_id}
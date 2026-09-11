from sqlalchemy.orm import Session
from app.exceptions.custom_exceptions import (
    ResourceNotFoundException,
    PermissionDeniedException,
    ResourceAlreadyExistsException,
)
from app.models.profile import FreelancerProfile
from app.models.user import User, UserRole
from app.repositories import profile_repo, skill_repo
from app.schemas.profile import FreelancerProfileCreate, FreelancerProfileUpdate
from app.exceptions.custom_exceptions import StockFlowException


def create_or_get_profile(
    db: Session, current_user: User, data: FreelancerProfileCreate
) -> FreelancerProfile:
    if current_user.role != UserRole.FREELANCER:
        raise PermissionDeniedException("Only freelancers can create a freelancer profile.")

    existing_profile = profile_repo.get_by_user_id(db, current_user.id)
    if existing_profile:
        raise ResourceAlreadyExistsException("FreelancerProfile", "user_id", current_user.id)

    profile = FreelancerProfile(
    user_id=current_user.id,
    bio=data.bio,
    hourly_rate=data.hourly_rate,
    experience=data.experience,
    availability=data.availability, 
)
    profile = profile_repo.create(db, profile, commit=False)
    db.flush()

    if data.skill_ids:
        profile_repo.set_skills(db, profile.id, data.skill_ids)

    db.commit()
    return profile_repo.get_by_user_id(db, current_user.id)


def update_profile(
    db: Session, current_user: User, data: FreelancerProfileUpdate
) -> FreelancerProfile:
    profile = profile_repo.get_by_user_id(db, current_user.id)
    if not profile:
        raise ResourceNotFoundException("FreelancerProfile", current_user.id)

    update_dict = data.model_dump(exclude_unset=True, exclude={"skill_ids"})
    for field, value in update_dict.items():
        setattr(profile, field, value)

    if data.skill_ids is not None:
        profile_repo.set_skills(db, profile.id, data.skill_ids)

    db.commit()
    return profile_repo.get_by_user_id(db, current_user.id)

def get_profile_by_user_id(db: Session, user_id: str) -> FreelancerProfile:
    profile = profile_repo.get_by_user_id(db, user_id)
    if not profile:
        raise ResourceNotFoundException("FreelancerProfile", user_id)
    return profile
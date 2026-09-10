from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.profile import (
    FreelancerProfileCreate,
    FreelancerProfileUpdate,
    FreelancerProfileResponse,
)
from app.repositories import profile_repo
from app.services import profile_service
from app.exceptions.custom_exceptions import ResourceNotFoundException
from decimal import Decimal
from fastapi import Query
from sqlalchemy.orm import joinedload
from app.models.profile import FreelancerProfile, FreelancerSkill



router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.post(
    "",
    response_model=FreelancerProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create freelancer profile",
)
def create_my_profile(
    data: FreelancerProfileCreate,
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    return profile_service.create_or_get_profile(db, current_user, data)


@router.get(
    "",
    response_model=FreelancerProfileResponse,
    summary="Get current freelancer profile",
)
def get_my_profile(
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    profile = profile_repo.get_by_user_id(db, current_user.id)
    if not profile:
        raise ResourceNotFoundException("FreelancerProfile", current_user.id)
    return profile


@router.patch(
    "",
    response_model=FreelancerProfileResponse,
    summary="Update freelancer profile",
)
def update_my_profile(
    data: FreelancerProfileUpdate,
    current_user: User = Depends(require_roles(UserRole.FREELANCER)),
    db: Session = Depends(get_db),
):
    return profile_service.update_profile(db, current_user, data)


@router.get(
    "/search",
    response_model=list[FreelancerProfileResponse],
    summary="Public directory to discover freelancers",
)
def search_freelancers(
    skill_id: int | None = Query(None, description="Filter by skill ID"),
    min_rate: Decimal | None = Query(None, ge=0, description="Minimum hourly rate"),
    max_rate: Decimal | None = Query(None, ge=0, description="Maximum hourly rate"),
    availability: str | None = Query(None, description="e.g., full_time, part_time"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(FreelancerProfile)

    if min_rate is not None:
        query = query.filter(FreelancerProfile.hourly_rate >= min_rate)
    if max_rate is not None:
        query = query.filter(FreelancerProfile.hourly_rate <= max_rate)
    if availability:
        query = query.filter(FreelancerProfile.availability.ilike(f"%{availability}%"))
    if skill_id is not None:
        query = (
            query.join(FreelancerSkill, FreelancerProfile.id == FreelancerSkill.profile_id)
            .filter(FreelancerSkill.skill_id == skill_id)
            .distinct()
        )

    return query.offset(skip).limit(limit).all()
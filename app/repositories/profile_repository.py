from sqlalchemy.orm import Session, joinedload
from app.models.profile import FreelancerProfile, FreelancerSkill
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[FreelancerProfile]):
    def __init__(self):
        super().__init__(FreelancerProfile)

    def get_by_user_id(self, db: Session, user_id: str) -> FreelancerProfile | None:
        return (
            db.query(FreelancerProfile)
            .options(
                joinedload(FreelancerProfile.skill_associations).joinedload(FreelancerSkill.skill)
            )
            .filter(FreelancerProfile.user_id == user_id)
            .first()
        )

    def set_skills(self, db: Session, profile_id: str, skill_ids: list[int]) -> None:
        db.query(FreelancerSkill).filter(FreelancerSkill.profile_id == profile_id).delete()
        for skill_id in set(skill_ids):
            db.add(FreelancerSkill(profile_id=profile_id, skill_id=skill_id))
        db.flush()


profile_repo = ProfileRepository()
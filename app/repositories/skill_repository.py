from sqlalchemy.orm import Session
from app.models.profile import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self):
        super().__init__(Skill)

    def get_all(self, db: Session) -> list[Skill]:
        return db.query(Skill).order_by(Skill.name.asc()).all()

    def get_by_name(self, db: Session, name: str) -> Skill | None:
        return db.query(Skill).filter(Skill.name.ilike(name.strip())).first()

    def get_by_name_excluding_id(self, db: Session, name: str, skill_id: int) -> Skill | None:
        return (
            db.query(Skill)
            .filter(Skill.name.ilike(name.strip()), Skill.id != skill_id)
            .first()
        )

    def delete(self, db: Session, skill: Skill) -> None:
        db.delete(skill)
        db.commit()


skill_repo = SkillRepository()
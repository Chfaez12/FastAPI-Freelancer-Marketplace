from typing import Generic, Type, TypeVar
from sqlalchemy.orm import Session
from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, id: any) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, obj: ModelType, commit: bool = True) -> ModelType:
        db.add(obj)
        if commit:
            db.commit()
            db.refresh(obj)
        return obj

    def delete(self, db: Session, obj: ModelType, commit: bool = True) -> None:
        db.delete(obj)
        if commit:
            db.commit()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
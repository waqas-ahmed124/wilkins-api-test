from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from fastapi_sqlalchemy import db

from apiserver.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    def __init__(self, model: ModelType):
        self.model = model

    def get(self, id: Any) -> Optional[ModelType]:
        return db.session.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: ModelType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def update(
        self, *, db_obj: ModelType, obj_in: Union[ModelType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> ModelType:
        obj = db.session.query(self.model).get(id)
        db.session.delete(obj)
        db.session.commit()
        return obj

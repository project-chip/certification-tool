from typing import Any, Dict, Generic, Optional, Sequence, Tuple, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDOperationNotSupported(Exception):
    """Can be raised when a base CRUD operation is not supported for a model"""


class CRUDBaseInit(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def select(self) -> Select[Tuple[ModelType]]:
        return select(self.model)


class CRUDBaseRead(Generic[ModelType], CRUDBaseInit[ModelType]):
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: Optional[int] = 0,
        limit: Optional[int] = 100,
        order_by: Optional[str] = None,
    ) -> Sequence[ModelType]:
        select = self.select()
        if order_by:
            select = select.order_by(order_by)
        else:
            select = select.order_by(self.model.id)
        return db.scalars(select.offset(skip).limit(limit)).all()


class CRUDBaseCreate(Generic[ModelType, CreateSchemaType], CRUDBaseInit[ModelType]):
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDBaseUpdate(Generic[ModelType, UpdateSchemaType], CRUDBaseInit[ModelType]):
    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDBaseDelete(Generic[ModelType], CRUDBaseInit[ModelType]):
    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        obj = db.get(self.model, id)
        if obj is not None:
            db.delete(obj)
            db.commit()
        return obj


class CRUDBase(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
    CRUDBaseCreate[ModelType, CreateSchemaType],
    CRUDBaseRead[ModelType],
    CRUDBaseUpdate[ModelType, UpdateSchemaType],
    CRUDBaseDelete[ModelType],
):
    pass

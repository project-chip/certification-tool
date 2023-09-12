from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.operator import OperatorCreate
from app.tests.utils.utils import random_lower_string


def create_random_operator(db: Session) -> models.Operator:
    name = random_lower_string()
    operator_in = OperatorCreate(name=name)
    return crud.operator.create(db=db, obj_in=operator_in)


operator_base_dict = {"name": "John Doe"}

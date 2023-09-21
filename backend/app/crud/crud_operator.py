from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.operator import Operator
from app.schemas.operator import OperatorCreate, OperatorUpdate


class CRUDOperator(CRUDBase[Operator, OperatorCreate, OperatorUpdate]):
    def get_by_name(self, db: Session, name: str) -> Optional[Operator]:
        query = self.select().where(Operator.name == name)
        return db.scalars(query).first()

    def get_or_create(self, db: Session, name: str, commit: bool = True) -> int:
        """
        Look for an Operator in the database with the same name. If none is found,
        create a new Operator.

        Args:
            db (Session): The database session
            name (str): The Operator name to use in the query
            commit (bool): Flag to indicate if the commit should be performed

        Returns:
            int: Operator ID
        """
        if operator := self.get_by_name(db=db, name=name):
            return operator.id

        operator = Operator(name=name)

        db.add(operator)
        db.flush()

        if commit:
            db.commit()

        return operator.id


operator = CRUDOperator(Operator)

from http import HTTPStatus
from typing import List, Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.db.session import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Operator])
def read_operators(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Sequence[models.Operator]:
    """Retrive list of operators.

    Args:
        skip (int, optional): Pagination offset. Defaults to 0.
        limit (int, optional): max number of records to return. Defaults to 100.

    Returns:
        List[Operator]: List of operators
    """
    return crud.operator.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.Operator)
def create_operator(
    *,
    db: Session = Depends(get_db),
    operator_in: schemas.OperatorCreate,
) -> models.Operator:
    """Create new operator.

    Args:
        operator_in (OperatorCreate): Parameters for new operator.

    Returns:
        Operator: newly created operator record
    """
    return crud.operator.create(db=db, obj_in=operator_in)


@router.put("/{id}", response_model=schemas.Operator)
def update_operator(
    *,
    db: Session = Depends(get_db),
    id: int,
    operator_in: schemas.OperatorUpdate,
) -> models.Operator:
    """Update an existing operator.

    Args:
        id (int): operator id
        operator_in (schemas.OperatorUpdate): operators parameters to be updated

    Raises:
        HTTPException: if no operator exists for provided operator id

    Returns:
        Operator: updated operator record
    """
    operator = crud.operator.get(db=db, id=id)
    if not operator:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Operator not found"
        )

    operator = crud.operator.update(db=db, db_obj=operator, obj_in=operator_in)
    return operator


@router.get("/{id}", response_model=schemas.Operator)
def read_operator(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> models.Operator:
    """Lookup operator by id.

    Args:
        id (int): operator id

    Raises:
        HTTPException: if no operator exists for provided operator id

    Returns:
        Operator: operator record
    """
    operator = crud.operator.get(db=db, id=id)
    if not operator:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Operator not found"
        )

    return operator


@router.delete("/{id}", response_model=schemas.Operator)
def delete_operator(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> models.Operator:
    """Lookup operator by id.

    Args:
        id (int): operator id

    Raises:
        HTTPException: if no operator exists for provided operator id

    Returns:
        Operator: operator record that was deleted
    """
    operator = crud.operator.remove(db=db, id=id)
    if not operator:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Operator not found"
        )

    return operator

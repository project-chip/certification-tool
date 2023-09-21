from http import HTTPStatus
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.db.session import get_db
from app.test_engine.test_script_manager import TestNotFound

router = APIRouter()


@router.get("/", response_model=List[schemas.TestRunConfig])
def read_test_run_configs(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve test_run_configs.
    """
    return crud.test_run_config.get_multi(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.TestRunConfig)
def create_test_run_config(
    *,
    db: Session = Depends(get_db),
    test_run_config_in: schemas.TestRunConfigCreate,
) -> Any:
    """
    Create new test run config.
    """
    try:
        return crud.test_run_config.create(db=db, obj_in=test_run_config_in)
    except TestNotFound as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f"Invalid test selection: {e}",
        )


@router.put("/{id}", response_model=schemas.TestRunConfig)
def update_test_run_config(
    *,
    db: Session = Depends(get_db),
    id: int,
    test_run_config_in: schemas.TestRunConfigUpdate,
) -> Any:
    """
    Update a test run config.
    """
    test_run_config = crud.test_run_config.get(db=db, id=id)
    if not test_run_config:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Test run config not found"
        )

    test_run_config = crud.test_run_config.update(
        db=db, db_obj=test_run_config, obj_in=test_run_config_in
    )
    return test_run_config


@router.get("/{id}", response_model=schemas.TestRunConfig)
def read_test_run_config(
    *,
    db: Session = Depends(get_db),
    id: int,
) -> Any:
    """
    Get test run config by ID.
    """
    test_run_config = crud.test_run_config.get(db=db, id=id)
    if not test_run_config:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Test run config not found"
        )

    return test_run_config

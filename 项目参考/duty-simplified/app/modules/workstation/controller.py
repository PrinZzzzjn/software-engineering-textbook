from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.workstation import service
from app.modules.workstation.param import WorkstationQueryParams
from app.modules.workstation.schema import WorkstationCreate, WorkstationOut

router = APIRouter(prefix="/workstations", tags=["哨位"])


@router.get("")
def list_workstations(
    params: WorkstationQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    return service.list_workstations(db, params)


@router.post("", response_model=WorkstationOut, status_code=status.HTTP_201_CREATED)
def create_workstation(data: WorkstationCreate, db: Session = Depends(get_db)):
    return service.create_workstation(db, data)


@router.get("/{workstation_id}", response_model=WorkstationOut)
def read_workstation(workstation_id: str, db: Session = Depends(get_db)):
    return service.get_workstation(db, workstation_id)


@router.put("/{workstation_id}", response_model=WorkstationOut)
def update_workstation(
    workstation_id: str, data: WorkstationCreate, db: Session = Depends(get_db)
):
    return service.update_workstation(db, workstation_id, data)


@router.delete("/{workstation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workstation(workstation_id: str, db: Session = Depends(get_db)):
    service.delete_workstation(db, workstation_id)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.personnel import service
from app.modules.personnel.param import PersonnelQueryParams
from app.modules.personnel.schema import PersonnelCreate, PersonnelOut

router = APIRouter(prefix="/personnel", tags=["人员"])


@router.get("")
def list_personnel(
    params: PersonnelQueryParams = Depends(),
    db: Session = Depends(get_db),
):
    return service.list_personnel(db, params)


@router.post("", response_model=PersonnelOut, status_code=status.HTTP_201_CREATED)
def create_personnel(data: PersonnelCreate, db: Session = Depends(get_db)):
    return service.create_personnel(db, data)


@router.get("/{certificate_number}", response_model=PersonnelOut)
def read_personnel(certificate_number: str, db: Session = Depends(get_db)):
    return service.get_personnel(db, certificate_number)


@router.put("/{certificate_number}", response_model=PersonnelOut)
def update_personnel(
    certificate_number: str, data: PersonnelCreate, db: Session = Depends(get_db)
):
    return service.update_personnel(db, certificate_number, data)


@router.delete("/{certificate_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_personnel(certificate_number: str, db: Session = Depends(get_db)):
    service.delete_personnel(db, certificate_number)

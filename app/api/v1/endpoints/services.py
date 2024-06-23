from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.service import Service
from app.models.user import User
from app.schemas.service import ServiceCreate, ServiceRead

router = APIRouter()


@router.post("/", response_model=ServiceRead)
def create_service(service: ServiceCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(get_current_user)):
    db_service = Service(**service.dict())
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.get("/{service_id}", response_model=ServiceRead)
def read_service(service_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service


@router.delete("/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_service = db.query(Service).filter(Service.id == service_id).first()
    if db_service:
        db.delete(db_service)
        db.commit()
    return {"ok": True}

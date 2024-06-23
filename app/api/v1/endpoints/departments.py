from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentRead

router = APIRouter()


@router.post("/", response_model=DepartmentRead)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    db_department = Department(**department.dict())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department


@router.get("/{department_id}", response_model=DepartmentRead)
def read_department(department_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if not db_department:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department


@router.delete("/{department_id}")
def delete_department(department_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    db_department = db.query(Department).filter(Department.id == department_id).first()
    if db_department:
        db.delete(db_department)
        db.commit()
    return {"ok": True}

from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_company
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyRead
from app.utils import upload_image_to_s3

router = APIRouter()


@router.post("/", response_model=CompanyRead)
async def create_company(company: CompanyCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    return crud_company.create_company(db=db, company=company)


@router.get("/", response_model=List[CompanyRead])
def list_companies(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return crud_company.get_companies(db=db)


@router.get("/{company_id}", response_model=CompanyRead)
def read_company(company_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_company = crud_company.get_company(db, company_id=company_id)
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@router.delete("/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    company = crud_company.delete_company(db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"ok": True}


@router.post("/{company_id}/upload-logo", response_model=CompanyRead)
async def upload_logo(company_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    company = crud_company.get_company(db, company_id=company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    logo_url = upload_image_to_s3(file, settings.AWS_S3_BUCKET_NAME)

    company.logo_url = logo_url
    db.commit()
    db.refresh(company)

    return company

from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.company import Company
from app.schemas.company import CompanyCreate


def create_company(db: Session, company: CompanyCreate):
    try:
        db_company = Company(**company.dict())
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return db_company
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Company with this CNPJ already exists")


def get_company(db: Session, company_id: int):
    return db.query(Company).filter(Company.id == company_id).first()


def delete_company(db: Session, company_id: int):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company:
        db.delete(company)
        db.commit()
    return company


def get_companies(db: Session) -> List[Company]:
    return db.query(Company).all()

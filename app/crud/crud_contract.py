from typing import List

from sqlalchemy import asc, desc
from sqlalchemy.orm import Session

from app.crud.crud_company import get_company
from app.models.contract import Contract
from app.models.contract_department import ContractDepartment
from app.models.contract_service import ContractService
from app.schemas.contract import ContractCreate
from app.schemas.department import DepartmentRead
from app.schemas.service import ServiceRead


def create_contract(db: Session, contract: ContractCreate):
    db_contract = Contract(
        start_date=contract.start_date,
        signature_date=contract.signature_date,
        rate=contract.rate,
        company_id=contract.company_id,
        active=True
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)

    for service_id in contract.services:
        db_contract_service = ContractService(contract_id=db_contract.id, service_id=service_id)
        db.add(db_contract_service)

    for department_id in contract.departments:
        db_contract_department = ContractDepartment(contract_id=db_contract.id, department_id=department_id)
        db.add(db_contract_department)

    db.commit()

    services = [ServiceRead.from_orm(cs.service) for cs in db_contract.services]
    departments = [DepartmentRead.from_orm(cd.department) for cd in db_contract.departments]
    company = get_company(db, db_contract.company_id)

    return {
        "id": db_contract.id,
        "start_date": db_contract.start_date,
        "signature_date": db_contract.signature_date,
        "rate": db_contract.rate,
        "company_id": db_contract.company_id,
        "services": services,
        "departments": departments,
        "company": company
    }


def get_contract(db: Session, contract_id: int):
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if db_contract:
        services = [ServiceRead.from_orm(cs.service) for cs in db_contract.services]
        departments = [DepartmentRead.from_orm(cd.department) for cd in db_contract.departments]
        company = get_company(db, db_contract.company_id)
        return {
            "id": db_contract.id,
            "start_date": db_contract.start_date,
            "signature_date": db_contract.signature_date,
            "rate": db_contract.rate,
            "company_id": db_contract.company_id,
            "services": services,
            "departments": departments,
            "company": company
        }
    return None


def get_all_contracts(db: Session, skip: int = 0, limit: int = 10, sort_by: str = "start_date",
                      sort_order: str = "asc") -> List[dict]:
    sort_function = asc if sort_order == "asc" else desc
    query = db.query(Contract).order_by(sort_function(getattr(Contract, sort_by))).offset(skip).limit(limit).all()
    contracts = []
    for db_contract in query:
        services = [ServiceRead.from_orm(cs.service) for cs in db_contract.services]
        departments = [DepartmentRead.from_orm(cd.department) for cd in db_contract.departments]
        company = get_company(db, db_contract.company_id)
        contracts.append({
            "id": db_contract.id,
            "start_date": db_contract.start_date,
            "signature_date": db_contract.signature_date,
            "rate": db_contract.rate,
            "company_id": db_contract.company_id,
            "services": services,
            "departments": departments,
            "company": company
        })
    return contracts


def delete_contract(db: Session, contract_id: int):
    db_contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if db_contract:
        db.delete(db_contract)
        db.commit()
        return True
    return False

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.crud import crud_contract
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.contract import Contract
from app.models.contract_service import ContractService
from app.models.service import Service
from app.models.user import User
from app.schemas.contract import ContractRead

router = APIRouter()


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_value = db.query(func.sum(Contract.rate)).filter(Contract.active == True).scalar() or 0
    active_contracts_count = db.query(Contract).filter(Contract.active == True).count()

    indicator_1 = db.query(Contract).filter(Contract.rate > 1).count() * 1.2

    indicator_2 = db.query(Contract).join(ContractService).join(Service).filter(
        func.lower(Service.name).like("%venda%")
    ).count()

    return {
        "total_value": total_value,
        "active_contracts_count": active_contracts_count,
        "indicator_1": indicator_1,
        "indicator_2": indicator_2,
    }


@router.get("/contracts", response_model=List[ContractRead])
def read_contracts(skip: int = 0, limit: int = 10, sort_by: str = "start_date", sort_order: str = "asc",
                   db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contracts = crud_contract.get_all_contracts(db, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order)
    return contracts

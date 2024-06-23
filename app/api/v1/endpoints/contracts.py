from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import crud_contract
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.contract import ContractCreate, ContractRead

router = APIRouter()


@router.post("/", response_model=ContractRead)
def create_contract(contract: ContractCreate, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    return crud_contract.create_contract(db=db, contract=contract)


@router.get("/{contract_id}", response_model=ContractRead)
def read_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_contract = crud_contract.get_contract(db, contract_id=contract_id)
    if db_contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return db_contract


@router.get("/", response_model=List[ContractRead])
def read_contracts(skip: int = 0, limit: int = 10, sort_by: str = "start_date", sort_order: str = "asc",
                   db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contracts = crud_contract.get_all_contracts(db, skip=skip, limit=limit, sort_by=sort_by, sort_order=sort_order)
    return contracts


@router.delete("/{contract_id}")
def delete_contract(contract_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    crud_contract.delete_contract(db, contract_id=contract_id)
    return {"ok": True}

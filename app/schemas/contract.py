from datetime import date
from typing import List

from pydantic import BaseModel, ConfigDict

from app.schemas.company import CompanyRead
from app.schemas.department import DepartmentRead
from app.schemas.service import ServiceRead


class ContractBase(BaseModel):
    start_date: date
    signature_date: date
    rate: float
    company_id: int


class ContractCreate(ContractBase):
    services: List[int]
    departments: List[int]


class ContractRead(ContractBase):
    id: int
    services: List[ServiceRead]
    departments: List[DepartmentRead]
    company: CompanyRead

    model_config = ConfigDict(from_attributes=True)

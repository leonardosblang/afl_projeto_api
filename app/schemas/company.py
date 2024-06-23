from pydantic import BaseModel


class CompanyBase(BaseModel):
    nickname: str
    trade_name: str
    legal_name: str
    cnpj: str
    state: str
    city: str


class CompanyCreate(CompanyBase):
    pass


class CompanyRead(CompanyBase):
    id: int
    logo_url: str | None = None

    class Config:
        orm_mode = True

from pydantic import BaseModel, ConfigDict


class ServiceBase(BaseModel):
    name: str
    department_id: int


class ServiceCreate(ServiceBase):
    pass


class ServiceRead(ServiceBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

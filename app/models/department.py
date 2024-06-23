from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    services = relationship("Service", back_populates="department")
    contracts = relationship("ContractDepartment", back_populates="department")

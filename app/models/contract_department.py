from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class ContractDepartment(Base):
    __tablename__ = 'contract_departments'

    contract_id = Column(Integer, ForeignKey('contracts.id'), primary_key=True)
    department_id = Column(Integer, ForeignKey('departments.id'), primary_key=True)

    contract = relationship("Contract", back_populates="departments")
    department = relationship("Department", back_populates="contracts")

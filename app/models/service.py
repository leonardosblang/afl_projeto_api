from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    department_id = Column(Integer, ForeignKey('departments.id'))

    department = relationship("Department", back_populates="services")
    contract_services = relationship("ContractService", back_populates="service")

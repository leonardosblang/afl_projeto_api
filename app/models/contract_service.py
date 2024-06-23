from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class ContractService(Base):
    __tablename__ = 'contract_services'

    contract_id = Column(Integer, ForeignKey('contracts.id'), primary_key=True)
    service_id = Column(Integer, ForeignKey('services.id'), primary_key=True)

    contract = relationship("Contract", back_populates="services")
    service = relationship("Service", back_populates="contract_services")

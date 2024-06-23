from sqlalchemy import Column, Integer, Date, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


class Contract(Base):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True, index=True)
    start_date = Column(Date)
    signature_date = Column(Date)
    rate = Column(Float)
    company_id = Column(Integer, ForeignKey('companies.id'))
    active = Column(Boolean, default=True)

    company = relationship("Company", back_populates="contracts")
    services = relationship("ContractService", back_populates="contract", cascade="all, delete-orphan")
    departments = relationship("ContractDepartment", back_populates="contract", cascade="all, delete-orphan")

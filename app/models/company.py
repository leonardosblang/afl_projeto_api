from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, index=True)
    trade_name = Column(String, index=True)
    legal_name = Column(String, index=True)
    cnpj = Column(String, unique=True, index=True)
    state = Column(String, index=True)
    city = Column(String, index=True)
    logo_url = Column(String)

    contracts = relationship("Contract", back_populates="company", cascade="all, delete-orphan")

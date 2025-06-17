from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base
from sqlalchemy import BigInteger

class Note(Base):
    __tablename__ = "notes"  # имя таблицы в базе данных

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

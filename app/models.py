from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base
from sqlalchemy import BigInteger

class Note(Base):
    __tablename__ = "notes"  # <= обязательно! имя таблицы

    id = Column(Integer, primary_key=True, index=True)  # <= Primary Key есть
    user_id = Column(BigInteger, index=True, nullable=False)
    title = Column(String(255), nullable=False)         # Заголовок
    description = Column(String, nullable=True)         # Описание может быть пустым
    created_at = Column(DateTime(timezone=True), server_default=func.now())

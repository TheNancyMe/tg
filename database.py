from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Получаем строку подключения из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаём сессию
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()

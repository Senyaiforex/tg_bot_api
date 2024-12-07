from os import getenv

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DOCKER = os.getenv("DOCKER")
user = os.getenv("POSTGRES_USER") if DOCKER else 'senyaiforex'
password = os.getenv("POSTGRES_PASSWORD") if DOCKER else 'senya2516'
db_name = os.getenv("POSTGRES_DB") if DOCKER else 'db'
db_host = os.getenv("POSTGRES_HOST") if DOCKER else '127.0.0.1'
db_port = os.getenv("POSTGRES_PORT") if DOCKER else '5432'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'postgresql+asyncpg://{user}:{password}@{db_host}:{db_port}/{db_name}'
engine = create_async_engine(DATABASE_URL,
                             pool_recycle=700,
                             pool_size=100,  # производительность
                             max_overflow=0,  # производительность
                             connect_args={"timeout": 20},
                             echo=False)
async_session = sessionmaker(engine,
                             expire_on_commit=False,
                             class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass

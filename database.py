from os import getenv

import sqlalchemy.ext.asyncio
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DOCKER = os.getenv("DOCKER")
user = os.getenv("POSTGRES_USER") if DOCKER else 'senyaiforex'
password = os.getenv("POSTGRES_PASSWORD") if DOCKER else 'senya2516'
db_name = os.getenv("POSTGRES_DB") if DOCKER else 'db'
db_host = os.getenv("POSTGRES_HOST") if DOCKER else '127.0.0.1'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'postgresql+asyncpg://{user}:{password}@{db_host}:5432/{db_name}'
engine = sqlalchemy.ext.asyncio.create_async_engine(DATABASE_URL,
                                                    pool_size=20,  # производительность
                                                    max_overflow=10, # производительность
                                                    connect_args={"timeout": 8},
                                                    echo=False)
async_session = sessionmaker(engine,
                             expire_on_commit=False,
                             class_=sqlalchemy.ext.asyncio.AsyncSession)


class Base(DeclarativeBase):
    pass

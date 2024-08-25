import sqlalchemy.ext.asyncio
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f'sqlite+aiosqlite:///{os.path.join(BASE_DIR, "app.db")}'
engine = sqlalchemy.ext.asyncio.create_async_engine(DATABASE_URL,
                                                    echo=True,
                                                    connect_args={"check_same_thread": False})
async_session = sessionmaker(engine,
                             expire_on_commit=False,
                             class_=sqlalchemy.ext.asyncio.AsyncSession)
Base = declarative_base()

import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config.settings import settings


engine = create_async_engine(settings.db_url, echo=False)
AsyncDBSession = async_sessionmaker(engine, expire_on_commit=False)



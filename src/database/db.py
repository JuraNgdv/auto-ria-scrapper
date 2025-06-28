import asyncio
import logging
import time

from sqlalchemy import text

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config.settings import settings


engine = create_async_engine(settings.db_url, echo=False)
AsyncDBSession = async_sessionmaker(engine, expire_on_commit=False)



async def wait_for_car_table(timeout: int = 60, delay: int = 5):
    logging.info("Checking if table 'cars' exists...")
    start_time = time.time()

    while True:
        async with engine.connect() as conn:
            result = await conn.execute(text(
                "SELECT to_regclass('public.cars')"
            ))
            table_exists = result.scalar()

            if table_exists:
                logging.info("Table 'cars' exists. Continuing execution.")
                return

        if time.time() - start_time > timeout:
            raise TimeoutError("Timed out waiting for table 'cars' to be created.")

        logging.warning("Table 'cars' not found. Retrying in %s seconds...", delay)
        await asyncio.sleep(delay)

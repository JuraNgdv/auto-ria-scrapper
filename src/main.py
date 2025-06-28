import asyncio
import logging

from src.config.settings import settings
from src.scheduler.scheduler import delayed_repeat_task, daily_task
from src.database.models import Base
from src.database.db import engine
from src.scraper import AutoRiaScraper
from src.utils.helpers import make_db_dump

log_level = logging.DEBUG if settings.DEBUG else logging.INFO
logging.basicConfig(level=log_level)
httpx_logger = logging.getLogger("httpx")
http_core_logger = logging.getLogger("httpcore")
aiosqlite_logger = logging.getLogger("aiosqlite")
httpx_logger.setLevel(logging.WARNING)
http_core_logger.setLevel(logging.WARNING)
aiosqlite_logger.setLevel(logging.WARNING)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    if settings.DEV_MODE:
        await init_db()
    await daily_task(make_db_dump, time_period=settings.DUMP_TIME)
    scraper = AutoRiaScraper(base_url=settings.START_URL, proxies=settings.PROXIES)
    await delayed_repeat_task(scraper.run, settings.SCRAPE_REPEAT_AFTER_MINUTES)

if __name__ == "__main__":
    asyncio.run(main())



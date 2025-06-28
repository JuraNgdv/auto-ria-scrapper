import asyncio
import logging
import time

import asyncpg
from httpx import AsyncClient
from sqlalchemy import insert
from typing import Optional, List
from fake_useragent import UserAgent
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import ProgrammingError

from src.config.settings import settings
from src.parsers.parser import AutoRiaParser
from src.database.db import AsyncDBSession
from src.database.models import Car
from src.utils.helpers import write_logs_table_header




class AutoRiaScraper:
    def __init__(self, base_url, proxies: Optional[List[str]] = None, max_concurrent_tasks: int = 5):
        self.base_url = base_url
        self.parser = AutoRiaParser()
        self.proxies = proxies or [None]
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.user_agent = UserAgent()


    async def start_worker(self, page: int, proxy: Optional[str]):
        async with self.semaphore:
            headers = {
                "User-Agent": self.user_agent.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
                "Connection": "keep-alive",
            }


            async with AsyncClient(headers=headers, trust_env=False, proxy=proxy) as client, AsyncDBSession() as connection:

                page_url = f"{self.base_url}?page={page}"
                links = await self.parser.parse_links_from_page(client, page_url)
                if not links:
                    return 0


                tasks = [self.parser.parse_car(client, url) for url in links]
                cars = await asyncio.gather(*tasks, return_exceptions=True)
                errors = []


                for car in cars:
                    if isinstance(car, Car):
                        await self.save_car(connection, car)
                        logging.debug(car.as_table_row())
                    else:
                        errors.append(car)
                if errors:
                    logging.info("Parsing exceptions on page - %s\n", page)
                for error in errors:
                    logging.info(error)
                logging.info("Parsed page - %s - %s\n", page, page_url)
                return len(cars)

    async def run(self):
        page = 1
        total_parsed = 0
        pages_parsed_count = 0
        start_time = time.time()
        logging.debug("\n%s\n\n%s", *write_logs_table_header(page))
        while True:
            tasks = [
                self.start_worker(page + i, proxy)
                for i, proxy in enumerate(self.proxies)
            ]
            results = await asyncio.gather(*tasks)
            parsed_count = sum(r for r in results if isinstance(r, int))

            if not parsed_count:
                break

            total_parsed += parsed_count
            pages_parsed_count += len(self.proxies)

            if settings.DEBUG and pages_parsed_count % 5 == 0:
                elapsed_minutes = (time.time() - start_time) / 60
                speed = total_parsed / elapsed_minutes if elapsed_minutes > 0 else 0
                logging.info(
                    f"[STATS] Parsed {total_parsed} items over {pages_parsed_count} pages in "
                    f"{elapsed_minutes:.2f} minutes → ~{speed:.2f} items/minute"
                )
                logging.debug("%s\n\n%s", *write_logs_table_header(page))

            page += len(self.proxies)



    async def save_car(self, connection, car: Car):
        values = {
            "url": car.url,
            "title": car.title,
            "price_usd": car.price_usd,
            "odometer": car.odometer,
            "username": car.username,
            "phone_number": car.phone_number,
            "image_url": car.image_url,
            "images_count": car.images_count,
            "car_number": car.car_number,
            "car_vin": car.car_vin,
            "datetime_found": car.datetime_found,
        }
        if settings.DEV_MODE:
            stmt = insert(Car).values(**values).prefix_with("OR REPLACE")
        else:
            stmt = pg_insert(Car).values(**values).on_conflict_do_update(
                index_elements=[Car.url],
                set_=values
            )
        await connection.execute(stmt)
        await connection.commit()

    async def save_car_with_retry(self, connection, stmt, max_retries=3, delay=20):
        for attempt in range(1, max_retries + 1):
            try:
                await connection.execute(stmt)
                return
            except ProgrammingError as e:
                if isinstance(e.orig, asyncpg.exceptions.UndefinedTableError):
                    logging.error(f"Cant find table? please migrate {attempt}/{max_retries}. Waiting {delay} sec...")
                    await asyncio.sleep(delay)
                else:
                    raise
        raise RuntimeError("Table still missing")
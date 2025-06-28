import asyncio
import logging
import traceback

import httpcore
from bs4 import BeautifulSoup
from datetime import datetime, UTC

from httpx import AsyncClient, HTTPStatusError

from src.config.settings import settings
from src.database.models import Car
from src.exceptions import MissingRequiredField
from src.parsers.errors.sold_error import DeletionBannerParser
from src.parsers.fields import (
    TitleParser,
    PriceParser,
    OdometerParser,
    UsernameParser,
    PhoneNumberParser,
    VinParser,
    CarNumberParser, ImageUrlsParser
)



class AutoRiaParser:
    async def fetch_html(self, client: AsyncClient, url: str, max_retries: int = 3, retry_delay: float = 2.0,
                         **kwargs) -> str | None:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.get(url, **kwargs)
                response.raise_for_status()
                return response.text

            except HTTPStatusError as e:
                if e.response.status_code == 429:
                    logging.warning(f"429 Too Many Requests for {url} — retrying {attempt}/{max_retries}...")
                    await asyncio.sleep(retry_delay)
                    continue
                raise

            except (httpcore.ReadTimeout, httpcore.ConnectTimeout) as e:
                logging.warning(f"Timeout for {url} — retrying {attempt}/{max_retries} - {e}")
                await asyncio.sleep(retry_delay)
                continue

            except Exception as e:
                logging.warning(f"Request failed for {url}: {type(e).__name__} — {e}")
                if settings.DEV_MODE:
                    traceback.print_exc()
                raise

        return None

    async def parse_car(self, client, url):
        html = await self.fetch_html(client, url)
        soup = BeautifulSoup(html, "html.parser")

        datetime_found = datetime.now(UTC)

        try:
            title = TitleParser.parse(soup)
            odometer = OdometerParser.parse(soup)
            price_usd = PriceParser.parse(soup)
            username = UsernameParser.parse(soup)
            phone_number = await PhoneNumberParser.parse(client, soup, car_url=url)
            car_vin = VinParser.parse(soup)
            image_urls = ImageUrlsParser.parse(soup)
            car_number = CarNumberParser.parse(soup)

            return Car(
                url=url,
                title=title,
                price_usd=price_usd,
                odometer=odometer,
                username=username,
                phone_number=phone_number,
                image_url=image_urls[0] if image_urls else None,
                images_count=len(image_urls),
                car_number=car_number,
                car_vin=car_vin,
                datetime_found=datetime_found
            )

        except MissingRequiredField as e:
            banner_text = DeletionBannerParser.parse(soup)
            if banner_text:
                return f"Parsing for {url} result - {banner_text}"
            return f"Failed to parse {e.field_name} {url}"
        except Exception as e:
            return f"Unexpected parsing error: {e}"

    async def parse_links_from_page(self, client, url, attempt=1, timeout=5, max_attempts=5):
        while attempt < max_attempts:
            try:
                html = await self.fetch_html(client, url)
                if not html:
                    return []
                soup = BeautifulSoup(html, "html.parser")
                return [tag['href'] for tag in soup.select("a.m-link-ticket")]
            except Exception as e:
                attempt += 1
                logging.warning(f"Links parse error for {url} — attempt {attempt} retrying in {timeout}, error: {e}")
                await asyncio.sleep(timeout)
                return await self.parse_links_from_page(client, url, attempt=attempt)



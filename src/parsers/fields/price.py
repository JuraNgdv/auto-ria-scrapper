from bs4 import BeautifulSoup

from src.exceptions import MissingRequiredField


class PriceParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> int:
        price = (
            PriceParser._from_price_value_strong(soup)
            or PriceParser._from_additional_block(soup)
            or PriceParser._from_old_template(soup)
            or 0
        )
        if not price:
            raise MissingRequiredField("price")
        return price

    @staticmethod
    def _from_price_value_strong(soup: BeautifulSoup) -> int:
        strong_tag = soup.select_one("div.price_value strong")
        if strong_tag and "$" in strong_tag.text:
            return PriceParser._clean_price(strong_tag.text)
        return 0

    @staticmethod
    def _from_additional_block(soup: BeautifulSoup) -> int:
        usd_tag = soup.select_one('div.price_value--additional [data-currency="USD"]')
        if usd_tag:
            return PriceParser._clean_price(usd_tag.text)
        return 0

    @staticmethod
    def _from_old_template(soup: BeautifulSoup) -> int:
        old_strong = soup.select_one("#basicInfoPriceWrapText strong")
        if old_strong and "$" in old_strong.text:
            return PriceParser._clean_price(old_strong.text)
        return 0

    @staticmethod
    def _clean_price(raw_text: str) -> int:
        try:
            return int(
                raw_text.replace("$", "").replace("€", "")
                .replace(" ", "").replace(" ", "")
                .replace(",", "").strip()
            )
        except ValueError:
            return 0

import re

from bs4 import BeautifulSoup
from src.exceptions import MissingRequiredField


class OdometerParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> int:
        odometer =  (
            OdometerParser._from_base_information(soup)
            or OdometerParser._from_basic_info_table(soup)
        )
        if not odometer:
            raise MissingRequiredField("odometer")
        return odometer

    @staticmethod
    def _extract_km(text: str) -> int:
        if "без пробігу" in text:
            return 0
        num = re.sub(r"[^\d]", "", text)
        try:
            if "тис" in text or "тыс" in text:
                return int(num) * 1000
            return int(num)
        except ValueError:
            return 0

    @staticmethod
    def _from_base_information(soup: BeautifulSoup) -> int:
        tag = soup.select_one("div.base-information")
        return OdometerParser._extract_km(tag.get_text()) if tag else 0

    @staticmethod
    def _from_basic_info_table(soup: BeautifulSoup) -> int:
        tag = soup.select_one("#basicInfoTableMainInfo0 span")
        return OdometerParser._extract_km(tag.get_text()) if tag else 0
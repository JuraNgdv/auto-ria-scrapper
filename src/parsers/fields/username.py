import time

from bs4 import BeautifulSoup

from src.exceptions import MissingRequiredField


class UsernameParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> str:
        username = (
                UsernameParser._from_div_or_h4(soup)
                or UsernameParser._from_new_version(soup)
        )
        if not username:
            raise MissingRequiredField("username")
        return username
    @staticmethod
    def _from_div_or_h4(soup: BeautifulSoup) -> str:
        tag = (
            soup.select_one("div.seller_info_name")
            or soup.select_one("h4.seller_info_name a")
        )
        return tag.get_text(strip=True) if tag else ""

    @staticmethod
    def _from_new_version(soup: BeautifulSoup) -> str:
        span = soup.select_one("#sellerInfoUserName span")
        return span.get_text(strip=True) if span else ""

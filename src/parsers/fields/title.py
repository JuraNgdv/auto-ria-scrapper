from bs4 import BeautifulSoup

from src.exceptions import MissingRequiredField


class TitleParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> str:
        title = (
            TitleParser._from_head(soup)
            or TitleParser._from_auto_head(soup)
            or TitleParser._from_basic_info(soup)
            or ""
        )
        if not title:
            raise MissingRequiredField("title")
        return title

    @staticmethod
    def _from_head(soup: BeautifulSoup) -> str:
        tag = soup.select_one("h1.head")
        return tag.get_text(strip=True) if tag else ""

    @staticmethod
    def _from_auto_head(soup: BeautifulSoup) -> str:
        tag = soup.select_one("h1.auto-head_title strong")
        return tag.get_text(strip=True) if tag else ""

    @staticmethod
    def _from_basic_info(soup: BeautifulSoup) -> str:
        tag = soup.select_one("#basicInfoTitle h1")
        return tag.get_text(strip=True) if tag else ""

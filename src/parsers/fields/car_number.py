from bs4 import BeautifulSoup


class CarNumberParser:


    @staticmethod
    def parse(soup: BeautifulSoup) -> str:
        car_number = (
            CarNumberParser._from_new_version(soup)
            or CarNumberParser._from_classic(soup)
            or None
        )
        return car_number

    @staticmethod
    def _from_new_version(soup: BeautifulSoup) -> str:
        tag = soup.select_one("div.car-number.ua span")
        return tag.get_text(strip=True) if tag else ""

    @staticmethod
    def _from_classic(soup: BeautifulSoup) -> str:
        outer = soup.select_one("span.state-num.ua")
        if not outer:
            return ""

        text = outer.find(text=True, recursive=False)
        return text.strip() if text else ""

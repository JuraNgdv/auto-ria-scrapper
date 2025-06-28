import json

from bs4 import BeautifulSoup



class VinParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> str:
        vin = (
                VinParser._from_badge(soup)
                or VinParser._from_label(soup)
                or VinParser._from_json_ld(soup)
                or None
        )
        return vin

    @staticmethod
    def _from_badge(soup: BeautifulSoup) -> str:
        for badge_id in ["badgesVin", "badgesVervin"]:
            tag = soup.select_one(f'span#{badge_id} span[class*="badge"]')
            if tag:
                vin = tag.get_text(strip=True)
                if vin:
                    return vin
        return ""

    @staticmethod
    def _from_label(soup: BeautifulSoup) -> str:
        for span_class in ["label-vin", "vin-code"]:
            tag = soup.select_one(f"span.{span_class}")
            if tag:
                texts = [t for t in tag.contents if isinstance(t, str)]
                if texts:
                    return texts[0].strip()
        return ""

    @staticmethod
    def _from_json_ld(soup: BeautifulSoup) -> str:
        script_tag = soup.select_one('script#ldJson2[type="application/ld+json"]')
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                return data.get("vehicleIdentificationNumber", "")
            except json.JSONDecodeError:
                pass
        return ""

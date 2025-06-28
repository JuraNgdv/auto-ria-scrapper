from bs4 import BeautifulSoup
from typing import List
from src.exceptions import MissingRequiredField
import json

class ImageUrlsParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> List[str]:
        urls = (
            ImageUrlsParser._from_img_tags(soup) or
            ImageUrlsParser._from_ld_json(soup)
        )
        if not urls:
            raise MissingRequiredField("image_urls")
        return urls

    @staticmethod
    def _from_img_tags(soup: BeautifulSoup) -> List[str]:
        container = soup.find("div", class_="carousel-inner")
        if not container:
            return []
        img_tags = container.find_all("img")
        urls = [img.get("src", "").strip() for img in img_tags if img.get("src")]
        return urls

    @staticmethod
    def _from_ld_json(soup: BeautifulSoup) -> List[str]:
        script = soup.find("script", type="application/ld+json")
        if not script or not script.string:
            return []
        try:
            data = json.loads(script.string)
            image_objects = data.get("image", [])
            urls = []
            for item in image_objects:
                if isinstance(item, dict):
                    url = item.get("contentUrl") or item.get("image")
                    if url:
                        urls.append(url)
            return urls
        except json.JSONDecodeError:
            return []

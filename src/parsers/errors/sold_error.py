from bs4 import BeautifulSoup


class DeletionBannerParser:
    @staticmethod
    def parse(soup: BeautifulSoup) -> str:
        banner = (
            DeletionBannerParser._from_auto_deleted_top_block(soup)
            or DeletionBannerParser._from_banner_status_text(soup)
            or ""
        )
        return banner

    @staticmethod
    def _from_auto_deleted_top_block(soup: BeautifulSoup) -> str:
        tag = soup.select_one("#autoDeletedTopBlock .notice_head")
        return tag.get_text(strip=True) if tag else ""

    @staticmethod
    def _from_banner_status_text(soup: BeautifulSoup) -> str:
        block = soup.select_one("#bannerStatusText")
        if block:
            texts = [el.get_text(strip=True) for el in block.find_all("span")]
            return " | ".join(texts)
        return ""

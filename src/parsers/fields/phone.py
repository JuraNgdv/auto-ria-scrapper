import asyncio
import re
import json
import logging

from bs4 import BeautifulSoup
from httpx import AsyncClient, TimeoutException, RequestError

from src.exceptions import MissingRequiredField


class PhoneNumberParser:
    @staticmethod
    async def parse(client, soup: BeautifulSoup, car_url: str) -> int:
            number = ''
            try:
                if soup.find("script", text=re.compile(r"__STATE__")):
                    number = await PhoneNumberParser._from_script_state(client, soup)
                else:
                    number = await PhoneNumberParser._from_dom_data(client, soup, car_url)
            except Exception as e:
                logging.warning(f"Failed to parse phone for {car_url}: {e}")

            if not number:
                raise MissingRequiredField("phone")
            return PhoneNumberParser._normalize_phone(number)

    @staticmethod
    def _normalize_phone(phone_str: str) -> int | None:
        digits = re.sub(r'\D', '', phone_str)

        if digits.startswith("0") and len(digits) == 10:
            digits = "38" + digits
        elif digits.startswith("380") and len(digits) == 12:
            pass
        else:
            logging.warning(f"Invalid phone format: {phone_str} -> {digits}")
            return None

        return int(digits)

    @staticmethod
    async def _from_dom_data(client, soup: BeautifulSoup, car_url: str) -> str:
        car_id_match = re.search(r"_(\d+)\.html", car_url)
        car_id = car_id_match.group(1) if car_id_match else None

        script_tag = soup.select_one('script[class^="js-user-secure-"]')
        if not script_tag:
            return ""
        script_class = script_tag.get("class", [""])[0]
        user_id = script_class.split("js-user-secure-")[-1]

        phone_tag = soup.select_one("[data-phone-id]")
        phone_id = phone_tag.get("data-phone-id") if phone_tag else None

        if not all([car_id, user_id, phone_id]):
            return ""

        json_data = PhoneNumberParser._build_payload(car_id, user_id, phone_id)
        return await PhoneNumberParser._make_request(client, json_data)

    @staticmethod
    async def _from_script_state(client, soup: BeautifulSoup) -> str:
        script_tag = soup.find("script", text=re.compile(r"window\.__STATE__\s*="))
        if not script_tag:
            return ""

        match = re.search(r"window\.__STATE__\s*=\s*({.*?});?\s*</script>", str(script_tag), re.DOTALL)
        if not match:
            return ""

        try:
            state_json = json.loads(match.group(1))
        except json.JSONDecodeError:
            return ""

        templates = (
            state_json
            .get("pageData", {})
            .get("structure", {})
            .values()
        )

        def find_action_data(obj):
            if isinstance(obj, dict):
                for key, val in obj.items():
                    if key == "buttons" and isinstance(val, list):
                        for btn in val:
                            if isinstance(btn, dict) and "actionData" in btn:
                                return btn["actionData"]
                    result = find_action_data(val)
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_action_data(item)
                    if result:
                        return result
            return None

        action_data = None
        for tmpl in templates:
            action_data = find_action_data(tmpl)
            if action_data:
                break

        if not action_data:
            return ""

        car_id = str(action_data.get("autoId"))
        data_list = action_data.get("data", [])
        data_dict = dict(data_list)

        user_id = data_dict.get("userId")
        phone_id = data_dict.get("phoneId")

        if not all([car_id, user_id, phone_id]):
            return ""

        json_data = PhoneNumberParser._build_payload(car_id, user_id, phone_id, params=data_dict)
        return await PhoneNumberParser._make_request(client, json_data)

    @staticmethod
    def _build_payload(car_id, user_id, phone_id, params=None):
        if params is None:
            params = {}

        base_params = {
            'userId': user_id,
            'phoneId': phone_id,
            'title': '',
            'isCheckedVin': '',
            'companyId': '',
            'companyEng': '',
            'avatar': '',
            'userName': '',
            'isCardPayer': '1',
            'dia': '',
            'isOnline': '',
            'isCompany': '',
            'workTime': '',
        }
        base_params.update(params)

        return {
            'blockId': 'autoPhone',
            'popUpId': 'autoPhone',
            'isLoginRequired': False,
            'isConfirmPhoneEmailRequired': False,
            'autoId': int(car_id),
            'params': base_params,
            'target': {},
            'formId': None,
            'langId': 4,
            'device': 'desktop-web',
        }

    @staticmethod
    async def _make_request(client: AsyncClient, json_data, max_retries: int = 3, retry_delay: float = 3.0) -> str:
        url = "https://auto.ria.com/bff/final-page/public/auto/popUp/"

        for attempt in range(1, max_retries + 1):
            try:
                resp = await client.post(url, json=json_data)

                if resp.status_code != 200:
                    await asyncio.sleep(retry_delay)
                    continue

                data = resp.json()
                phone = data.get("additionalParams", {}).get("phoneStr", "")
                if not phone:
                    logging.warning(f"_make_request no phone, {json_data=} {data=}")
                return phone

            except (TimeoutException, RequestError) as e:
                logging.warning(f"Request error attempt {attempt}/{max_retries}: {e}")
                await asyncio.sleep(retry_delay)
            except Exception as e:
                logging.exception(f"Unexpected exception in _make_request: {e}")
                break

        return ""


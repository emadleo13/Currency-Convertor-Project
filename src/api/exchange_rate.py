import requests

from src.utils.constants import API_BASE_URL, REQUEST_TIMEOUT


class ExchangeRateError(Exception):
    pass


class NetworkError(ExchangeRateError):
    pass


class APIError(ExchangeRateError):
    pass


class ExchangeRateAPI:
    def __init__(self):
        self._session = requests.Session()

    def get_rates(self, base_currency: str) -> dict:
        url = f"{API_BASE_URL}{base_currency}"
        try:
            response = self._session.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 429:
                raise APIError("تعداد درخواست‌ها بیش از حد مجاز است")
            response.raise_for_status()
            data = response.json()

            if data.get("result") != "success":
                raise APIError(f"خطای API: {data.get('result')}")

            return {
                "rates": data["rates"],
                "base": data["base_code"],
                "last_updated": data["time_last_update_utc"],
            }
        except requests.ConnectionError:
            raise NetworkError("اتصال به اینترنت برقرار نیست")
        except requests.Timeout:
            raise NetworkError("زمان درخواست به پایان رسید")
        except requests.HTTPError as e:
            raise NetworkError(f"خطای HTTP: {e.response.status_code}")

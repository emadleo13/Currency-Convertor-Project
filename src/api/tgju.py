import requests
from bs4 import BeautifulSoup

from src.utils.constants import TGJU_URL, REQUEST_TIMEOUT


class TgjuError(Exception):
    pass


class NetworkError(TgjuError):
    pass


class ScrapingError(TgjuError):
    pass


TGJU_KEY_TO_ISO = {
    "price_dollar_rl": "USD",
    "price_eur": "EUR",
    "price_gbp": "GBP",
    "price_aed": "AED",
    "price_try": "TRY",
    "price_chf": "CHF",
    "price_cny": "CNY",
    "price_jpy": "JPY",
    "price_cad": "CAD",
    "price_aud": "AUD",
    "price_nzd": "NZD",
    "price_sgd": "SGD",
    "price_inr": "INR",
    "price_pkr": "PKR",
    "price_iqd": "IQD",
    "price_sar": "SAR",
    "price_kwd": "KWD",
    "price_bhd": "BHD",
    "price_omr": "OMR",
    "price_qar": "QAR",
    "price_krw": "KRW",
    "price_dkk": "DKK",
    "price_sek": "SEK",
    "price_nok": "NOK",
    "price_rub": "RUB",
    "price_thb": "THB",
    "price_myr": "MYR",
    "price_hkd": "HKD",
    "price_afn": "AFN",
    "price_azn": "AZN",
    "price_amd": "AMD",
    "price_gel": "GEL",
    "price_kgs": "KGS",
    "price_tjs": "TJS",
    "price_tmt": "TMT",
    "price_syp": "SYP",
}


class TgjuScraper:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })

    def get_irr_rates(self) -> dict[str, float]:
        try:
            response = self._session.get(TGJU_URL, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
        except requests.ConnectionError:
            raise NetworkError("اتصال به اینترنت برقرار نیست")
        except requests.Timeout:
            raise NetworkError("زمان درخواست به پایان رسید")
        except requests.HTTPError as e:
            raise NetworkError(f"خطای HTTP: {e.response.status_code}")

        return self._parse_rates(response.text)

    def _parse_rates(self, html: str) -> dict[str, float]:
        soup = BeautifulSoup(html, "html.parser")
        rows = soup.find_all("tr", attrs={"data-market-row": True})

        if not rows:
            raise ScrapingError("داده‌ای از سایت دریافت نشد")

        rates = {}
        for row in rows:
            key = row.get("data-market-row", "")
            price_str = row.get("data-price", "")
            iso_code = TGJU_KEY_TO_ISO.get(key)

            if iso_code and price_str:
                try:
                    price = float(price_str.replace(",", ""))
                    rates[iso_code] = price
                except ValueError:
                    continue

        if not rates:
            raise ScrapingError("نرخ ارزی استخراج نشد")

        return rates

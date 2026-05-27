from src.api.exchange_rate import ExchangeRateAPI
from src.api.tgju import TgjuScraper


class CurrencyConverter:
    def __init__(self):
        self._exchange_api = ExchangeRateAPI()
        self._tgju = TgjuScraper()
        self._irr_rates: dict[str, float] = {}
        self._exchange_rates: dict[str, float] = {}
        self._exchange_base: str = ""

    def fetch_irr_rates(self) -> None:
        self._irr_rates = self._tgju.get_irr_rates()

    def fetch_exchange_rates(self, base_currency: str) -> str:
        data = self._exchange_api.get_rates(base_currency)
        self._exchange_rates = data["rates"]
        self._exchange_base = data["base"]
        return data["last_updated"]

    def convert(self, amount: float, from_code: str, to_code: str) -> float:
        if from_code == to_code:
            return amount

        if from_code == "IRR" or to_code == "IRR":
            return self._convert_with_irr(amount, from_code, to_code)

        return self._convert_international(amount, from_code, to_code)

    def _convert_with_irr(self, amount: float, from_code: str, to_code: str) -> float:
        if not self._irr_rates:
            self.fetch_irr_rates()

        if from_code == "IRR":
            rate_per_unit = self._irr_rates.get(to_code)
            if rate_per_unit is not None:
                return amount / rate_per_unit
            # Cross-rate: IRR -> USD -> target
            usd_rate = self._irr_rates.get("USD")
            if usd_rate is None:
                raise ValueError(f"نرخ {to_code} موجود نیست")
            amount_usd = amount / usd_rate
            return self._convert_international(amount_usd, "USD", to_code)
        else:
            rate_per_unit = self._irr_rates.get(from_code)
            if rate_per_unit is not None:
                return amount * rate_per_unit
            # Cross-rate: source -> USD -> IRR
            usd_rate = self._irr_rates.get("USD")
            if usd_rate is None:
                raise ValueError(f"نرخ {from_code} موجود نیست")
            amount_usd = self._convert_international(amount, from_code, "USD")
            return amount_usd * usd_rate

    def _convert_international(self, amount: float, from_code: str, to_code: str) -> float:
        if not self._exchange_rates or self._exchange_base != from_code:
            self.fetch_exchange_rates(from_code)

        rate = self._exchange_rates.get(to_code)
        if rate is None:
            raise ValueError(f"نرخ {to_code} موجود نیست")
        return amount * rate

    def get_rate(self, from_code: str, to_code: str) -> float:
        return self.convert(1.0, from_code, to_code)

    @property
    def has_irr_rates(self) -> bool:
        return bool(self._irr_rates)

    @property
    def has_exchange_rates(self) -> bool:
        return bool(self._exchange_rates)

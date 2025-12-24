from decimal import Decimal
from dataclasses import dataclass
from typing import Optional
from .currency import Currency


@dataclass
class ExchangeRates:
    id: Optional[int] = None
    rate: Optional[Decimal] = None
    base_currency: Optional[Currency] = None
    target_currency: Optional[Currency] = None

    def __str__(self):
        return f"ExchangeRates{{id={self.id}, rate={self.rate}, baseCurrency={self.base_currency}, targetCurrency={self.target_currency}}}"


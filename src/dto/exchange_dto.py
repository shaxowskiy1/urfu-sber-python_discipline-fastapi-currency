from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import Optional
from ..models.currency import Currency


@dataclass
class ExchangeDTO:
    id: Optional[int] = None
    rate: Optional[Decimal] = None
    base_currency: Optional[Currency] = None
    target_currency: Optional[Currency] = None
    amount: Optional[Decimal] = None
    converted_amount: Optional[Decimal] = None

    def get_converted_amount(self) -> Decimal:
        if self.amount is not None and self.rate is not None:
            self.converted_amount = (self.amount * self.rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        return self.converted_amount

    def __str__(self):
        return f"ExchangeRates{{id={self.id}, rate={self.rate}, baseCurrency={self.base_currency}, targetCurrency={self.target_currency}}}"


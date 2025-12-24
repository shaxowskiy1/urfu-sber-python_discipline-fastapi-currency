from ..dto.exchange_dto import ExchangeDTO
from ..models.exchange_rates import ExchangeRates


class MappingDTO:

    @staticmethod
    def map_to_exchange_dto(exchange_rates: ExchangeRates) -> ExchangeDTO:
        exchange_dto = ExchangeDTO()
        exchange_dto.id = exchange_rates.id
        exchange_dto.base_currency = exchange_rates.base_currency
        exchange_dto.target_currency = exchange_rates.target_currency
        exchange_dto.rate = exchange_rates.rate
        return exchange_dto

    @staticmethod
    def map_to_exchange_rates_entity(exchange_dto: ExchangeDTO) -> ExchangeRates:
        exchange_rates = ExchangeRates()
        exchange_rates.id = exchange_dto.id
        exchange_rates.base_currency = exchange_dto.base_currency
        exchange_rates.target_currency = exchange_dto.target_currency
        exchange_rates.rate = exchange_dto.rate
        return exchange_rates


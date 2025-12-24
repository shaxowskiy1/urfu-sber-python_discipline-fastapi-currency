import json
from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal
from ..models.exchange_rates import ExchangeRates
from ..models.currency import Currency
from ..config.redis import get_redis_client


class ExchangeRatesService(ABC):
    @abstractmethod
    def create_exchange_rate(self, exchange_rates: ExchangeRates) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[ExchangeRates]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[ExchangeRates]:
        pass

    @abstractmethod
    def find_all(self) -> List[ExchangeRates]:
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> None:
        pass


class ExchangeRatesServiceImpl(ExchangeRatesService):

    def __init__(self, exchange_rates_repository):
        self.exchange_rates_repository = exchange_rates_repository
        self.redis_client = get_redis_client()
        self.cache_ttl = 3600  

    def find_all(self) -> List[ExchangeRates]:
        cache_key = self._get_cache_key_all()
        cached_value = self._get_from_cache_list(cache_key)
        if cached_value is not None:
            return cached_value
        
        exchange_rates_list = self.exchange_rates_repository.find_all()
        if exchange_rates_list:
            self._set_to_cache_list(cache_key, exchange_rates_list)
        return exchange_rates_list

    def delete_by_id(self, id: int) -> None:
        exchange_rate = self.exchange_rates_repository.find_by_id(id)
        self.exchange_rates_repository.delete(id)
        self._delete_from_cache(self._get_cache_key_by_id(id))
        if exchange_rate and exchange_rate.base_currency and exchange_rate.target_currency:
            if exchange_rate.base_currency.code and exchange_rate.target_currency.code:
                name_key = f"{exchange_rate.base_currency.code}{exchange_rate.target_currency.code}"
                self._delete_from_cache(self._get_cache_key_by_name(name_key))
        self._clear_all_cache()

    def update_exchange_rate(self, exchange_rates: ExchangeRates, id: int) -> None:
        old_exchange = self.exchange_rates_repository.find_by_id(id)
        exchange_to_be_updated = self.exchange_rates_repository.find_by_id(id)
        exchange_to_be_updated.rate = exchange_rates.rate
        exchange_to_be_updated.base_currency = exchange_rates.base_currency
        exchange_to_be_updated.target_currency = exchange_rates.target_currency
        self.exchange_rates_repository.update(exchange_to_be_updated, id)
        self._clear_all_cache()



    def create_exchange_rate(self, exchange_rates: ExchangeRates) -> None:
        new_exchange_rates = ExchangeRates(
            base_currency=exchange_rates.base_currency,
            target_currency=exchange_rates.target_currency,
            rate=exchange_rates.rate
        )
        self.exchange_rates_repository.create(new_exchange_rates)
        self._clear_all_cache()

    def find_by_id(self, id: int) -> Optional[ExchangeRates]:
        cache_key = self._get_cache_key_by_id(id)
        cached_value = self._get_from_cache(cache_key)
        if cached_value:
            return cached_value
        
        exchange_rate = self.exchange_rates_repository.find_by_id(id)
        if exchange_rate:
            self._set_to_cache(cache_key, exchange_rate)
        return exchange_rate

    def find_by_name(self, name: str) -> Optional[ExchangeRates]:
        cache_key = self._get_cache_key_by_name(name)
        cached_value = self._get_from_cache(cache_key)
        if cached_value:
            return cached_value
        
        exchange_rate = self.exchange_rates_repository.find_by_name(name)
        if exchange_rate:
            self._set_to_cache(cache_key, exchange_rate)
            if exchange_rate.id:
                id_cache_key = self._get_cache_key_by_id(exchange_rate.id)
                self._set_to_cache(id_cache_key, exchange_rate)
        return exchange_rate

    def _get_cache_key_by_id(self, id: int) -> str:
        return f"exchange_rate:id:{id}"

    def _get_cache_key_by_name(self, name: str) -> str:
        return f"exchange_rate:name:{name}"

    def _get_cache_key_all(self) -> str:
        return "exchange_rate:all"

    def _currency_to_dict(self, currency: Currency) -> dict:
        return {
            "id": currency.id,
            "code": currency.code,
            "fullname": currency.fullname,
            "sign": currency.sign
        }

    def _dict_to_currency(self, data: dict) -> Currency:
        currency = Currency()
        currency.id = data.get("id")
        currency.code = data.get("code")
        currency.fullname = data.get("fullname")
        currency.sign = data.get("sign")
        return currency

    def _exchange_rates_to_dict(self, exchange_rate: ExchangeRates) -> dict:
        return {
            "id": exchange_rate.id,
            "rate": str(exchange_rate.rate) if exchange_rate.rate else None,
            "base_currency": self._currency_to_dict(exchange_rate.base_currency) if exchange_rate.base_currency else None,
            "target_currency": self._currency_to_dict(exchange_rate.target_currency) if exchange_rate.target_currency else None
        }

    def _dict_to_exchange_rates(self, data: dict) -> ExchangeRates:
        exchange_rate = ExchangeRates()
        exchange_rate.id = data.get("id")
        exchange_rate.rate = Decimal(str(data.get("rate"))) if data.get("rate") else None
        base_currency_data = data.get("base_currency")
        if base_currency_data:
            exchange_rate.base_currency = self._dict_to_currency(base_currency_data)
        target_currency_data = data.get("target_currency")
        if target_currency_data:
            exchange_rate.target_currency = self._dict_to_currency(target_currency_data)
        return exchange_rate

    def _get_from_cache(self, key: str) -> Optional[ExchangeRates]:
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                data = json.loads(cached_data)
                return self._dict_to_exchange_rates(data)
        except Exception as e:
            pass
        return None

    def _get_from_cache_list(self, key: str) -> Optional[List[ExchangeRates]]:
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                data_list = json.loads(cached_data)
                return [self._dict_to_exchange_rates(item) for item in data_list]
        except Exception as e:
            pass
        return None

    def _set_to_cache(self, key: str, exchange_rate: ExchangeRates) -> None:
        try:
            data = self._exchange_rates_to_dict(exchange_rate)
            json_data = json.dumps(data, ensure_ascii=False)
            self.redis_client.setex(key, self.cache_ttl, json_data)
        except Exception as e:
            pass

    def _set_to_cache_list(self, key: str, exchange_rates_list: List[ExchangeRates]) -> None:
        try:
            data_list = [self._exchange_rates_to_dict(er) for er in exchange_rates_list]
            json_data = json.dumps(data_list, ensure_ascii=False)
            self.redis_client.setex(key, self.cache_ttl, json_data)
        except Exception as e:
            pass

    def _delete_from_cache(self, key: str) -> None:
        try:
            self.redis_client.delete(key)
        except Exception as e:
            pass

    def _clear_all_cache(self) -> None:
        self._delete_from_cache(self._get_cache_key_all())
    


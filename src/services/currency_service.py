import json
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.currency import Currency
from ..config.redis import get_redis_client


class CurrencyService(ABC):
    @abstractmethod
    def create_currency(self, currency: Currency) -> None:
        pass

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[Currency]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Currency]:
        pass

    @abstractmethod
    def find_all(self) -> List[Currency]:
        pass

    @abstractmethod
    def delete_by_id(self, id: int) -> None:
        pass

    @abstractmethod
    def update_currency(self, currency: Currency, id: int) -> None:
        pass


class CurrencyServiceImpl(CurrencyService):
    def __init__(self, currency_repository):
        self.currency_repository = currency_repository
        self.redis_client = get_redis_client()
        self.cache_ttl = 3600  

    def create_currency(self, currency: Currency) -> None:
        new_currency = self._set_meaning_in_currency(currency.code, currency.fullname, currency.sign)
        self.currency_repository.create(new_currency)
        self._clear_all_cache()

    def find_by_id(self, id: int) -> Optional[Currency]:
        cache_key = self._get_cache_key_by_id(id)
        cached_value = self._get_from_cache(cache_key)
        if cached_value:
            return cached_value
                currency = self.currency_repository.find_by_id(id)
        if currency:
            self._set_to_cache(cache_key, currency)
        return currency

    def find_by_name(self, name: str) -> Optional[Currency]:
        cache_key = self._get_cache_key_by_code(name)
        cached_value = self._get_from_cache(cache_key)
        if cached_value:
            return cached_value
        
        currency = self.currency_repository.find_by_name(name)
        if currency:
            self._set_to_cache(cache_key, currency)
            if currency.id:
                id_cache_key = self._get_cache_key_by_id(currency.id)
                self._set_to_cache(id_cache_key, currency)
        return currency

    def find_all(self) -> List[Currency]:
        cache_key = self._get_cache_key_all()
        cached_value = self._get_from_cache_list(cache_key)
        if cached_value is not None:
            return cached_value
        
        currencies = self.currency_repository.find_all()
        if currencies:
            self._set_to_cache_list(cache_key, currencies)
        return currencies

    def delete_by_id(self, id: int) -> None:
        currency = self.currency_repository.find_by_id(id)
        self.currency_repository.delete(id)
        self._delete_from_cache(self._get_cache_key_by_id(id))
        if currency and currency.code:
            self._delete_from_cache(self._get_cache_key_by_code(currency.code))
        self._clear_all_cache()

    def update_currency(self, currency: Currency, id: int) -> None:
        old_currency = self.currency_repository.find_by_id(id)
        currency_to_be_updated = self.currency_repository.find_by_id(id)
        currency_to_be_updated.fullname = currency.fullname
        currency_to_be_updated.code = currency.code
        currency_to_be_updated.sign = currency.sign
        self.currency_repository.update(currency_to_be_updated, id)

    @staticmethod
    def _set_meaning_in_currency(code: str, fullname: str, sign: str) -> Currency:
        currency = Currency()
        currency.code = code
        currency.fullname = fullname
        currency.sign = sign
        return currency

    def _get_cache_key_by_id(self, id: int) -> str:
        return f"currency:id:{id}"

    def _get_cache_key_by_code(self, code: str) -> str:
        return f"currency:code:{code}"

    def _get_cache_key_all(self) -> str:
        return "currency:all"

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

    def _get_from_cache(self, key: str) -> Optional[Currency]:
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                data = json.loads(cached_data)
                return self._dict_to_currency(data)
        except Exception as e:
            pass
        return None

    def _get_from_cache_list(self, key: str) -> Optional[List[Currency]]:
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                data_list = json.loads(cached_data)
                return [self._dict_to_currency(item) for item in data_list]
        except Exception as e:
            pass
        return None

    def _set_to_cache(self, key: str, currency: Currency) -> None:
        try:
            data = self._currency_to_dict(currency)
            json_data = json.dumps(data, ensure_ascii=False)
            self.redis_client.setex(key, self.cache_ttl, json_data)
        except Exception as e:
            pass

    def _set_to_cache_list(self, key: str, currencies: List[Currency]) -> None:
        try:
            data_list = [self._currency_to_dict(currency) for currency in currencies]
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


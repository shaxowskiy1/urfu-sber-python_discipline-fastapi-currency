from typing import List, Optional
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from ..models.exchange_rates import ExchangeRates
from ..models.currency import Currency
from .crud_repository import CrudRepository
from ..config.database import get_db_connection


class ExchangeRatesRepository(CrudRepository[ExchangeRates, int]):

    def __init__(self):
        self.data_source = get_db_connection

    def find_by_id(self, id: int) -> Optional[ExchangeRates]:
        query = """
            SELECT
                e.id AS id,
                baseCurrency.id AS baseCurrencyId,
                baseCurrency.fullname AS baseCurrencyName,
                baseCurrency.code AS baseCurrencyCode,
                baseCurrency.sign AS baseCurrencySign,
                targetCurrency.id AS targetCurrencyId,
                targetCurrency.fullname AS targetCurrencyName,
                targetCurrency.code AS targetCurrencyCode,
                targetCurrency.sign AS targetCurrencySign,
                e.rate AS rate
            FROM
                exchangerates e
                    JOIN
                currencies baseCurrency ON e.basecurrencyid = baseCurrency.id
                    JOIN
                currencies targetCurrency ON e.targetcurrencyid = targetCurrency.id
            WHERE e.id = %s
        """
        exchange_rates = None
        try:
            with self.data_source() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (id,))
                    row = cursor.fetchone()
                    if row:
                        exchange_rates = self._parse_from_result_set(row)
        except Exception as e:
            raise RuntimeError(f"Ошибка при поиске курса обмена по id: {e}")
        return exchange_rates

    def find_by_name(self, name: str) -> Optional[ExchangeRates]:
        query = """
            SELECT
                e.id AS id,
                baseCurrency.id AS baseCurrencyId,
                baseCurrency.fullname AS baseCurrencyName,
                baseCurrency.code AS baseCurrencyCode,
                baseCurrency.sign AS baseCurrencySign,
                targetCurrency.id AS targetCurrencyId,
                targetCurrency.fullname AS targetCurrencyName,
                targetCurrency.code AS targetCurrencyCode,
                targetCurrency.sign AS targetCurrencySign,
                e.rate AS rate
            FROM
                exchangerates e
                    JOIN
                currencies baseCurrency ON e.basecurrencyid = baseCurrency.id
                    JOIN
                currencies targetCurrency ON e.targetcurrencyid = targetCurrency.id
            WHERE concat(baseCurrency.code, targetCurrency.code) = %s
        """
        exchange_rates = None
        try:
            with self.data_source() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (name,))
                    row = cursor.fetchone()
                    if row:
                        exchange_rates = self._parse_from_result_set(row)
        except Exception as e:
            raise RuntimeError(f"Ошибка при поиске курса обмена по имени: {e}")
        return exchange_rates

    def find_all(self) -> List[ExchangeRates]:
        exchange_rates_list = []
        query = """
            SELECT
                e.id AS id,
                baseCurrency.id AS baseCurrencyId,
                baseCurrency.fullname AS baseCurrencyName,
                baseCurrency.code AS baseCurrencyCode,
                baseCurrency.sign AS baseCurrencySign,
                targetCurrency.id AS targetCurrencyId,
                targetCurrency.fullname AS targetCurrencyName,
                targetCurrency.code AS targetCurrencyCode,
                targetCurrency.sign AS targetCurrencySign,
                e.rate AS rate
            FROM
                exchangerates e
                    JOIN
                currencies baseCurrency ON e.basecurrencyid = baseCurrency.id
                    JOIN
                currencies targetCurrency ON e.targetcurrencyid = targetCurrency.id
        """
        try:
            with self.data_source() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    for row in rows:
                        exchange_rates = self._parse_from_result_set(row)
                        exchange_rates_list.append(exchange_rates)
                        print(exchange_rates)
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении всех курсов обмена: {e}")
        return exchange_rates_list

    def create(self, exchange_rates: ExchangeRates) -> None:
        query = "INSERT INTO exchangerates (basecurrencyid, targetcurrencyid, rate) VALUES (%s, %s, %s)"
        connection = None
        try:
            with self.data_source() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        query,
                        (
                            exchange_rates.base_currency.id,
                            exchange_rates.target_currency.id,
                            exchange_rates.rate
                        )
                    )
                    connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            raise RuntimeError(f"Ошибка при создании курса обмена: {e}")

    def delete(self, id: int) -> None:
        query = "DELETE FROM exchangerates WHERE id=%s"
        connection = None
        try:
            with self.data_source() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (id,))
                    connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            raise RuntimeError(f"Ошибка при удалении курса обмена: {e}")

    @staticmethod
    def _parse_from_result_set(row) -> ExchangeRates:
        base_currency = Currency()
        target_currency = Currency()
        
        if isinstance(row, dict):
            base_currency.id = row.get('basecurrencyid')
            base_currency.fullname = row.get('basecurrencyname')
            base_currency.code = row.get('basecurrencycode')
            base_currency.sign = row.get('basecurrencysign')

            target_currency.id = row.get('targetcurrencyid')
            target_currency.fullname = row.get('targetcurrencyname')
            target_currency.code = row.get('targetcurrencycode')
            target_currency.sign = row.get('targetcurrencysign')

            exchange_rates = ExchangeRates()
            exchange_rates.id = row.get('id')
            exchange_rates.rate = Decimal(str(row.get('rate'))) if row.get('rate') else None
        else:
            base_currency.id = row[1]
            base_currency.fullname = row[2]
            base_currency.code = row[3]
            base_currency.sign = row[4]

            target_currency.id = row[5]
            target_currency.fullname = row[6]
            target_currency.code = row[7]
            target_currency.sign = row[8]

            exchange_rates = ExchangeRates()
            exchange_rates.id = row[0]
            exchange_rates.rate = Decimal(str(row[9])) if row[9] else None

        exchange_rates.base_currency = base_currency
        exchange_rates.target_currency = target_currency

        return exchange_rates


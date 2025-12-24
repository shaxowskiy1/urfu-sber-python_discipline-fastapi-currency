import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from ..models.currency import Currency
from .crud_repository import CrudRepository
from ..config.database import get_db_connection


class CurrencyRepository(CrudRepository[Currency, int]):
    def __init__(self):
        self.data_source = get_db_connection

    def find_by_id(self, id: int) -> Optional[Currency]:
        query = "SELECT * FROM currencies WHERE id=%s"
        currency = None
        try:
            with self.data_source() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (id,))
                    row = cursor.fetchone()
                    if row:
                        currency = self._parse_from_result_set(row)
        except Exception as e:
            raise RuntimeError(f"Ошибка при поиске валюты по id: {e}")
        return currency

    def find_by_name(self, name: str) -> Optional[Currency]:
        query = "SELECT * FROM currencies WHERE code=%s"
        currency = None
        try:
            with self.data_source() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, (name,))
                    row = cursor.fetchone()
                    if row:
                        currency = self._parse_from_result_set(row)
        except Exception as e:
            raise RuntimeError(f"Ошибка при поиске валюты по имени: {e}")
        return currency

    def find_all(self) -> List[Currency]:
        currency_list = []
        try:
            with self.data_source() as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = "SELECT * FROM currencies"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    for row in rows:
                        currency = self._parse_from_result_set(row)
                        currency_list.append(currency)
        except Exception as e:
            raise RuntimeError(f"Ошибка при получении всех валют: {e}")
        return currency_list

    def create(self, currency: Currency) -> None:
        query = "INSERT INTO currencies (code, fullname, sign) VALUES (%s, %s, %s)"
        connection = None
        try:
            with self.data_source() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (currency.code, currency.fullname, currency.sign))
                    connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            raise RuntimeError(f"Ошибка при создании валюты: {e}")

    def update(self, currency: Currency, id: int) -> None:
        query = "UPDATE currencies SET code=%s, fullname=%s, sign=%s WHERE id=%s"
        connection = None
        try:
            with self.data_source() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (currency.code, currency.fullname, currency.sign, id))
                    connection.commit()
        except Exception as e:
            if connection: 
                connection.rollback()
            raise RuntimeError(f"Ошибка при обновлении валюты: {e}")

    def delete(self, id: int) -> None:
        query = "DELETE FROM currencies WHERE id=%s"
        connection = None
        try:
            with self.data_source() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (id,))
                    connection.commit()
        except Exception as e:
            if connection:
                connection.rollback()
            raise RuntimeError(f"Ошибка при удалении валюты: {e}")

    @staticmethod
    def _parse_from_result_set(row) -> Currency:
        currency = Currency()
        if isinstance(row, dict):
            currency.id = row.get('id')
            currency.code = row.get('code')
            currency.fullname = row.get('fullname')
            currency.sign = row.get('sign')
        else:
            currency.id = row[0]
            currency.code = row[1]
            currency.fullname = row[2]
            currency.sign = row[3]
        return currency


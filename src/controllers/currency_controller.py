from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..models.currency import Currency
from ..services.currency_service import CurrencyServiceImpl
from ..repositories.currency_repository import CurrencyRepository

currency_router = APIRouter(tags=["currencies"])

currency_repository = CurrencyRepository()
currency_service = CurrencyServiceImpl(currency_repository)


class CurrencyRequest(BaseModel):
    code: str
    fullname: str
    sign: str

    class Config:
        from_attributes = True


class CurrencyResponse(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    fullname: Optional[str] = None
    sign: Optional[str] = None

    class Config:
        from_attributes = True


@currency_router.get("/currencies", response_model=List[CurrencyResponse])
def find_all():
    currencies = currency_service.find_all()
    return [CurrencyResponse(**currency.__dict__) for currency in currencies]


@currency_router.get("/currency/{id}", response_model=CurrencyResponse)
def find_by_id(id: int):
    currency = currency_service.find_by_id(id)
    if currency is None:
        raise HTTPException(status_code=404, detail="Валюта не найдена")
    return CurrencyResponse(**currency.__dict__)


@currency_router.get("/currency", response_model=CurrencyResponse)
def find_by_name(name: str):
    currency = currency_service.find_by_name(name)
    if currency is None:
        raise HTTPException(status_code=404, detail="Валюта не найдена")
    return CurrencyResponse(**currency.__dict__)


@currency_router.post("/currencies", status_code=201)
def post_currency(currency: CurrencyRequest):
    currency_obj = Currency(
        code=currency.code,
        fullname=currency.fullname,
        sign=currency.sign
    )
    currency_service.create_currency(currency_obj)
    return {"message": "Валюта успешно создана"}


@currency_router.patch("/currencies/{id}", status_code=200)
def update_currency(currency: CurrencyRequest, id: int):
    currency_obj = Currency(
        code=currency.code,
        fullname=currency.fullname,
        sign=currency.sign
    )
    currency_service.update_currency(currency_obj, id)
    return {"message": "Валюта успешно обновлена"}


@currency_router.delete("/currencies/{id}", status_code=204)
def delete_currency(id: int):
    currency_service.delete_by_id(id)
    return None


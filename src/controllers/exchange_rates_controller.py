from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel
from ..models.exchange_rates import ExchangeRates
from ..models.currency import Currency
from ..dto.exchange_dto import ExchangeDTO
from ..services.exchange_rates_service import ExchangeRatesServiceImpl
from ..repositories.exchange_rates_repository import ExchangeRatesRepository
from ..util.mapping_dto import MappingDTO

exchange_rates_router = APIRouter(tags=["exchange_rates"])

exchange_rates_repository = ExchangeRatesRepository()
exchange_rates_service = ExchangeRatesServiceImpl(exchange_rates_repository)


class CurrencyModel(BaseModel):
    id: Optional[int] = None
    code: Optional[str] = None
    fullname: Optional[str] = None
    sign: Optional[str] = None


class ExchangeRatesRequest(BaseModel):
    rate: Decimal
    base_currency: CurrencyModel
    target_currency: CurrencyModel


class ExchangeRatesResponse(BaseModel):
    id: Optional[int] = None
    rate: Optional[Decimal] = None
    base_currency: Optional[CurrencyModel] = None
    target_currency: Optional[CurrencyModel] = None


class ExchangeDTOResponse(BaseModel):
    id: Optional[int] = None
    rate: Optional[Decimal] = None
    base_currency: Optional[CurrencyModel] = None
    target_currency: Optional[CurrencyModel] = None
    amount: Optional[Decimal] = None
    converted_amount: Optional[Decimal] = None


@exchange_rates_router.get("/exchangeRates", response_model=List[ExchangeRatesResponse])
def find_all():
    exchange_rates_list = exchange_rates_service.find_all()
    result = []
    for er in exchange_rates_list:
        result.append(ExchangeRatesResponse(
            id=er.id,
            rate=er.rate,
            base_currency=CurrencyModel(**er.base_currency.__dict__),
            target_currency=CurrencyModel(**er.target_currency.__dict__)
        ))
    return result


@exchange_rates_router.get("/exchangeRate", response_model=ExchangeRatesResponse)
def find_by_name(name: str):
    exchange_rates = exchange_rates_service.find_by_name(name)
    if exchange_rates is None:
        raise HTTPException(status_code=404, detail="Курс обмена не найден")
    return ExchangeRatesResponse(
        id=exchange_rates.id,
        rate=exchange_rates.rate,
        base_currency=CurrencyModel(**exchange_rates.base_currency.__dict__),
        target_currency=CurrencyModel(**exchange_rates.target_currency.__dict__)
    )


@exchange_rates_router.get("/exchangeRate/{id}", response_model=ExchangeRatesResponse)
def find_by_id(id: int):
    exchange_rates = exchange_rates_service.find_by_id(id)
    if exchange_rates is None:
        raise HTTPException(status_code=404, detail="Курс обмена не найден")
    return ExchangeRatesResponse(
        id=exchange_rates.id,
        rate=exchange_rates.rate,
        base_currency=CurrencyModel(**exchange_rates.base_currency.__dict__),
        target_currency=CurrencyModel(**exchange_rates.target_currency.__dict__)
    )


@exchange_rates_router.post("/exchangeRates", status_code=201)
def post_exchange_rate(exchange_rates: ExchangeRatesRequest):
    base_currency = Currency(
        id=exchange_rates.base_currency.id,
        code=exchange_rates.base_currency.code,
        fullname=exchange_rates.base_currency.fullname,
        sign=exchange_rates.base_currency.sign
    )
    target_currency = Currency(
        id=exchange_rates.target_currency.id,
        code=exchange_rates.target_currency.code,
        fullname=exchange_rates.target_currency.fullname,
        sign=exchange_rates.target_currency.sign
    )
    exchange_rates_obj = ExchangeRates(
        base_currency=base_currency,
        target_currency=target_currency,
        rate=exchange_rates.rate
    )
    exchange_rates_service.create_exchange_rate(exchange_rates_obj)
    return {"message": "Курс обмена успешно создан"}


@exchange_rates_router.delete("/exchangeRates/{id}", status_code=204)
def delete_exchange_rate(id: int):
    exchange_rates_service.delete_by_id(id)
    return None


@exchange_rates_router.get("/exchange", response_model=ExchangeDTOResponse)
def exchange(
    from_currency: str = Query(..., alias="from"),
    to: str = Query(...),
    amount: Decimal = Query(...)
):
    exchange_rates_by_name = exchange_rates_service.find_by_name(from_currency + to)
    if exchange_rates_by_name is None:
        raise HTTPException(status_code=404, detail="Курс обмена не найден")
    
    exchange_dto = MappingDTO.map_to_exchange_dto(exchange_rates_by_name)
    exchange_dto.amount = amount
    exchange_dto.converted_amount = (amount * exchange_dto.rate).quantize(
        Decimal('0.01'), rounding=ROUND_HALF_UP
    )
    
    return ExchangeDTOResponse(
        id=exchange_dto.id,
        rate=exchange_dto.rate,
        base_currency=CurrencyModel(**exchange_dto.base_currency.__dict__),
        target_currency=CurrencyModel(**exchange_dto.target_currency.__dict__),
        amount=exchange_dto.amount,
        converted_amount=exchange_dto.converted_amount
    )


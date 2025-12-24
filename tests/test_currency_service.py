import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.currency_service import CurrencyServiceImpl
from src.models.currency import Currency


class TestCurrencyService:

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def mock_redis_client(self):
        mock_client = Mock()
        mock_client.get.return_value = None
        mock_client.setex.return_value = True
        mock_client.delete.return_value = 1
        return mock_client

    @pytest.fixture
    def currency_service(self, mock_repository, mock_redis_client):
        with patch('src.services.currency_service.get_redis_client', return_value=mock_redis_client):
            service = CurrencyServiceImpl(mock_repository)
            service.redis_client = mock_redis_client
            return service

    def test_find_by_id_cache_hit(self, currency_service, mock_repository, mock_redis_client):
        currency_id = 1
        cached_currency = Currency(id=1, code="USD", fullname="US Dollar", sign="$")
        
        import json
        cached_data = json.dumps({
            "id": 1,
            "code": "USD",
            "fullname": "US Dollar",
            "sign": "$"
        }, ensure_ascii=False)
        mock_redis_client.get.return_value = cached_data
        
        result = currency_service.find_by_id(currency_id)
        
        assert result is not None
        assert result.id == 1
        assert result.code == "USD"
        assert result.fullname == "US Dollar"
        assert result.sign == "$"
        mock_redis_client.get.assert_called_once_with(f"currency:id:{currency_id}")
        mock_repository.find_by_id.assert_not_called()

    def test_find_by_id_cache_miss(self, currency_service, mock_repository, mock_redis_client):
        currency_id = 1
        currency_from_db = Currency(id=1, code="USD", fullname="US Dollar", sign="$")
        
        mock_redis_client.get.return_value = None
        mock_repository.find_by_id.return_value = currency_from_db
        
        result = currency_service.find_by_id(currency_id)
        
        assert result is not None
        assert result.id == 1
        assert result.code == "USD"
        assert result.fullname == "US Dollar"
        assert result.sign == "$"
        mock_redis_client.get.assert_called_once_with(f"currency:id:{currency_id}")
        mock_repository.find_by_id.assert_called_once_with(currency_id)
        mock_redis_client.setex.assert_called_once()

    def test_create_currency(self, currency_service, mock_repository, mock_redis_client):
        new_currency = Currency(code="EUR", fullname="Euro", sign="€")
        mock_repository.create.return_value = None
        
        currency_service.create_currency(new_currency)
        
        mock_repository.create.assert_called_once()
        created_currency = mock_repository.create.call_args[0][0]
        assert created_currency.code == "EUR"
        assert created_currency.fullname == "Euro"
        assert created_currency.sign == "€"
        

        mock_redis_client.delete.assert_called_once_with("currency:all")

    def test_create_currency_with_none_values(self, currency_service, mock_repository, mock_redis_client):

        new_currency = Currency(code="GBP", fullname=None, sign=None)
        mock_repository.create.return_value = None

        currency_service.create_currency(new_currency)

        mock_repository.create.assert_called_once()
        created_currency = mock_repository.create.call_args[0][0]
        assert created_currency.code == "GBP"
        assert created_currency.fullname is None
        assert created_currency.sign is None
        mock_redis_client.delete.assert_called_once_with("currency:all")


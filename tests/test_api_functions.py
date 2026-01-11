"""Тесты для API функций."""

import pytest
from unittest.mock import patch, Mock
import os

from src.utils import get_currency_rates, get_stock_prices


def test_get_currency_rates_with_api():
    """Тест получения курсов валют через API."""
    with patch('src.utils.requests.get') as mock_get:
        # Мокаем успешный ответ API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'base': 'USD',
            'rates': {
                'USD': 1.0,
                'EUR': 0.85,
                'GBP': 0.75
            }
        }
        mock_get.return_value = mock_response

        # Устанавливаем тестовый API ключ
        os.environ['EXCHANGE_RATE_API_KEY'] = 'test_key'

        result = get_currency_rates(['USD', 'EUR', 'GBP'])

        assert len(result) == 3
        assert result[0]['currency'] == 'USD'
        assert isinstance(result[0]['rate'], float)


def test_get_currency_rates_api_error():
    """Тест получения курсов валют при ошибке API."""
    with patch('src.utils.requests.get') as mock_get:
        # Мокаем ошибку API
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = get_currency_rates(['USD', 'EUR'])

        # Должны получить заглушечные значения
        assert len(result) == 2
        assert result[0]['currency'] == 'USD'


def test_get_stock_prices_with_api():
    """Тест получения цен акций через API."""
    with patch('src.utils.requests.get') as mock_get:
        # Мокаем успешный ответ API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{'price': 185.25}]
        mock_get.return_value = mock_response

        # Устанавливаем тестовый API ключ
        os.environ['STOCK_API_KEY'] = 'test_key'

        result = get_stock_prices(['AAPL'])

        assert len(result) == 1
        assert result[0]['stock'] == 'AAPL'
        assert result[0]['price'] == 185.25


def test_get_stock_prices_no_api_key():
    """Тест получения цен акций без API ключа."""
    # Удаляем API ключ
    if 'STOCK_API_KEY' in os.environ:
        del os.environ['STOCK_API_KEY']

    result = get_stock_prices(['AAPL', 'MSFT'])

    # Должны получить заглушечные значения
    assert len(result) == 2
    assert all(isinstance(item['price'], float) for item in result)


@pytest.mark.parametrize("stocks,expected_count", [
    (['AAPL', 'MSFT'], 2),
    ([], 0),
    (['UNKNOWN'], 1),
])
def test_get_stock_prices_stub(stocks, expected_count):
    """Параметризованный тест заглушки цен акций."""
    from src.utils import get_stock_prices_stub

    result = get_stock_prices_stub(stocks)

    assert len(result) == expected_count
    if expected_count > 0:
        assert result[0]['stock'] == stocks[0].upper()

"""
Тесты для реальных API функций.
"""

import os
from unittest.mock import Mock, patch

import pytest

from src.utils import get_currency_rates, get_stock_prices


@pytest.mark.skipif(
    not os.environ.get("EXCHANGE_RATE_API_KEY"),
    reason="Требуется API ключ для курсов валют"
)
def test_real_currency_rates():
    """Тест реального API курсов валют."""
    currencies = ["USD", "EUR", "GBP"]
    result = get_currency_rates(currencies)
    
    assert isinstance(result, list)
    assert len(result) > 0
    
    for item in result:
        assert "currency" in item
        assert "rate" in item
        assert isinstance(item["rate"], (int, float))
        assert item["rate"] > 0


@pytest.mark.skipif(
    not os.environ.get("STOCK_API_KEY"),
    reason="Требуется API ключ для акций"
)
def test_real_stock_prices():
    """Тест реального API цен акций."""
    stocks = ["AAPL", "MSFT"]
    result = get_stock_prices(stocks)
    
    assert isinstance(result, list)
    assert len(result) > 0
    
    for item in result:
        assert "stock" in item
        assert "price" in item
        assert isinstance(item["price"], (int, float))
        assert item["price"] > 0


def test_currency_rates_fallback():
    """Тест fallback для курсов валют."""
    with patch('src.utils.os.environ.get', return_value=''):
        currencies = ["USD", "EUR"]
        result = get_currency_rates(currencies)
        
        assert isinstance(result, list)
        assert len(result) == len(currencies)
        
        for item in result:
            assert "currency" in item
            assert "rate" in item


def test_stock_prices_fallback():
    """Тест fallback для цен акций."""
    with patch('src.utils.os.environ.get', return_value=''):
        stocks = ["AAPL", "MSFT"]
        result = get_stock_prices(stocks)
        
        assert isinstance(result, list)
        assert len(result) == len(stocks)
        
        for item in result:
            assert "stock" in item
            assert "price" in item
            assert item["price"] > 0

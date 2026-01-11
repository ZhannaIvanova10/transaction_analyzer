import pytest
import os
from unittest.mock import Mock, patch
from src.utils import get_stock_prices


class TestAdditionalCoverage:
    """Дополнительные тесты для увеличения покрытия кода."""

    def test_get_stock_prices_basic(self):
        """Базовый тест получения цен акций"""
        with patch('src.utils.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'AAPL': {'price': 185.0}}
            mock_get.return_value = mock_response

            os.environ['STOCK_API_KEY'] = 'test_key'
            result = get_stock_prices(['AAPL'])

            assert len(result) == 1
            assert result[0]['stock'] == 'AAPL'
            assert result[0]['price'] == 185.0

    def test_get_stock_prices_no_api_key(self):
        """Тест получения цен акций без API ключа"""
        os.environ.pop('STOCK_API_KEY', None)
        result = get_stock_prices(['AAPL'])
        # При отсутствии ключа возвращаются фиктивные данные
        assert len(result) == 1
        assert result[0]['stock'] == 'AAPL'
        assert isinstance(result[0]['price'], (int, float))

    def test_get_stock_prices_empty_list(self):
        """Тест получения цен для пустого списка акций"""
        result = get_stock_prices([])
        assert result == []

    def test_get_stock_prices_api_error(self):
        """Тест получения цен при ошибке API"""
        with patch('src.utils.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            os.environ['STOCK_API_KEY'] = 'test_key'
            result = get_stock_prices(['AAPL'])
            # Функция возвращает список словарей при ошибке API
            assert len(result) == 1
            assert isinstance(result, list)
            assert isinstance(result[0], dict)
            assert 'stock' in result[0]
            assert 'price' in result[0]
            assert result[0]['stock'] == 'AAPL'
            assert isinstance(result[0]['price'], (int, float))


"""
Тесты для модуля views.py
"""
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.views import get_home_page_data, get_events_page_data


class TestViews:
    """Тесты для функций представлений."""
    
    def test_get_home_page_data_success(self):
        """Тест успешного получения данных главной страницы."""
        date_str = "2024-01-15 14:30:00"
        
        with patch('src.views.load_user_settings') as mock_settings:
            mock_settings.return_value = {
                "user_currencies": ["USD", "EUR"],
                "user_stocks": ["AAPL", "TSLA"]
            }
            result = get_home_page_data(date_str)
            
            assert "greeting" in result
            assert "cards" in result
            assert "currency_rates" in result
            assert "stock_prices" in result
            assert isinstance(result["greeting"], str)
            assert isinstance(result["cards"], list)
    
    @pytest.fixture
    def sample_dataframe(self):
        """Фикстура с тестовым DataFrame."""
        return pd.DataFrame({
            'Дата операции': pd.to_datetime([
                '2024-01-01', '2024-01-02', '2024-01-03',
                '2024-01-04', '2024-01-05'
            ]),
            'Сумма платежа': [-100, -200, 300, -150, 500],
            'Категория': [
                'Супермаркеты', 'Кафе', 'Зарплата',
                'Транспорт', 'Подарок'
            ],
            'Описание': [
                'Покупка продуктов', 'Обед', 'Начисление ЗП',
                'Такси', 'День рождения'
            ]
        })
    def test_get_events_page_data_monthly(self, sample_dataframe):
        """Тест получения данных событий за месяц."""
        date_str = "2024-01-31 23:59:59"
        
        with patch('src.views.load_user_settings') as mock_settings:
            mock_settings.return_value = {
                "user_currencies": ["USD"],
                "user_stocks": ["AAPL"]
            }
            
            result = get_events_page_data(sample_dataframe, date_str, "M")
            
            assert "expenses" in result
            assert "income" in result
            assert "currency_rates" in result
            assert "stock_prices" in result
            
            # Проверяем структуру expenses
            assert "total_amount" in result["expenses"]
            assert "main" in result["expenses"]
            assert "transfers_and_cash" in result["expenses"]
            
            # Проверяем структуру income
            assert "total_amount" in result["income"]
            assert "main" in result["income"]
    @pytest.mark.parametrize("period", ["W", "M", "Y", "ALL"])
    def test_get_events_page_data_all_periods(self, sample_dataframe, period):
        """Тест получения данных событий для всех периодов."""
        date_str = "2024-01-15 12:00:00"
        
        with patch('src.views.load_user_settings') as mock_settings:
            mock_settings.return_value = {"user_currencies": [], "user_stocks": []}
            
            result = get_events_page_data(sample_dataframe, date_str, period)
            
            assert isinstance(result, dict)
            assert "expenses" in result
            assert "income" in result
    
    def test_get_events_page_data_empty_dataframe(self):
        """Тест обработки пустого DataFrame."""
        empty_df = pd.DataFrame()
        date_str = "2024-01-15 12:00:00"
        result = get_events_page_data(empty_df, date_str, "M")
        
        assert result["expenses"]["total_amount"] == 0
        assert result["income"]["total_amount"] == 0
        assert len(result["expenses"]["main"]) == 0
        assert len(result["income"]["main"]) == 0

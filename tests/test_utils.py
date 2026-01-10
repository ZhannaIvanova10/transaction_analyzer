"""
Тесты для модуля utils.py
"""
import pytest
from datetime import datetime
from unittest.mock import patch, mock_open
import json
import pandas as pd

from src.utils import (
    get_greeting_by_time,
    parse_date,
    filter_transactions_by_date_range,
    load_user_settings
)
class TestUtils:
    """Тесты для утилитарных функций."""
    
    def test_get_greeting_by_time_morning(self):
        """Тест приветствия для утра."""
        morning_time = datetime(2024, 1, 1, 8, 0, 0)
        assert get_greeting_by_time(morning_time) == "Доброе утро"
    
    def test_get_greeting_by_time_afternoon(self):
        """Тест приветствия для дня."""
        afternoon_time = datetime(2024, 1, 1, 14, 0, 0)
        assert get_greeting_by_time(afternoon_time) == "Добрый день"
    
    def test_get_greeting_by_time_evening(self):
        """Тест приветствия для вечера."""
        evening_time = datetime(2024, 1, 1, 20, 0, 0)
        assert get_greeting_by_time(evening_time) == "Добрый вечер"
    def test_get_greeting_by_time_night(self):
        """Тест приветствия для ночи."""
        night_time = datetime(2024, 1, 1, 2, 0, 0)
        assert get_greeting_by_time(night_time) == "Доброй ночи"
    
    def test_parse_date_valid(self):
        """Тест парсинга валидной даты."""
        date_str = "2024-01-15 14:30:00"
        result = parse_date(date_str)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
        assert result.hour == 14
        assert result.minute == 30
    
    def test_parse_date_invalid(self):
        """Тест парсинга невалидной даты."""
        date_str = "invalid-date"
        with pytest.raises(ValueError):
            parse_date(date_str)
    def test_filter_transactions_by_date_range(self):
        """Тест фильтрации транзакций по дате."""
        # Создаем тестовые данные
        df = pd.DataFrame({
            'Дата операции': pd.to_datetime([
                '2024-01-01',
                '2024-01-15',
                '2024-02-01',
                '2024-03-01'
            ]),
            'Сумма': [100, 200, 300, 400]
        })
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        result = filter_transactions_by_date_range(df, start_date, end_date)
        
        assert len(result) == 2
        assert result['Дата операции'].dt.year.iloc[0] == 2024
        assert result['Дата операции'].dt.month.iloc[0] == 1
    @patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
    @patch("json.load")
    def test_load_user_settings_success(self, mock_json_load, mock_file):
        """Тест успешной загрузки пользовательских настроек."""
        mock_json_load.return_value = {"user_currencies": ["USD", "EUR"]}
        
        result = load_user_settings()
        
        assert "user_currencies" in result
        assert result["user_currencies"] == ["USD", "EUR"]
        mock_file.assert_called_once_with('user_settings.json', 'r', encoding='utf-8')
    
    @patch("builtins.open", side_effect=FileNotFoundError())
    def test_load_user_settings_file_not_found(self, mock_file):
        """Тест загрузки настроек при отсутствии файла."""
        result = load_user_settings()
        
        assert "user_currencies" in result
        assert result["user_currencies"] == ["USD", "EUR"]

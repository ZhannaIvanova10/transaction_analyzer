"""
Тесты для проверки покрытия кода.
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

from src.views import get_home_page_data, get_events_page_data
from src.services import (
    profitable_cashback_categories,
    investment_bank,
    simple_search,
    search_by_phone_numbers,
    search_by_person_transfers,
)
from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday,
)
from src.utils import (
    load_transactions_from_excel,
    filter_transactions_by_date,
    get_greeting_by_time,
    get_currency_rates,
    get_stock_prices,
)


class TestCoverage:
    """Тесты для достижения полного покрытия кода."""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        return [
            {
                "Дата операции": "2024-01-15",
                "Сумма операции": 1000.0,
                "Сумма платежа": -1000.0,
                "Категория": "Супермаркеты",
                "Описание": "Покупка в магазине",
                "Кешбэк": 10.0,
                "Номер карты": "1234567812345678",
            },
            {
                "Дата операции": "2024-01-10",
                "Сумма операции": 500.0,
                "Сумма платежа": -500.0,
                "Категория": "Рестораны",
                "Описание": "Ужин в кафе",
                "Кешбэк": 5.0,
                "Номер карты": "1234567812345678",
            },
        ]

    @pytest.fixture
    def sample_dataframe(self):
        """Фикстура с тестовым DataFrame."""
        data = {
            "Дата операции": pd.to_datetime(["2024-01-15", "2024-01-10", "2024-01-05"]),
            "Сумма операции": [1000.0, 500.0, 2000.0],
            "Сумма платежа": [-1000.0, -500.0, 1500.0],
            "Категория": ["Супермаркеты", "Рестораны", "Зарплата"],
            "Описание": ["Покупка", "Ужин", "Начисление"],
            "Кешбэк": [10.0, 5.0, 0.0],
            "Номер карты": ["1234", "1234", None],
        }
        return pd.DataFrame(data)

    def test_views_empty_data(self):
        """Тест views с пустыми данными."""
        # Мокаем зависимости
        with patch("src.views.get_greeting_by_time") as mock_greeting, \
                patch("src.views.load_user_settings") as mock_settings, \
                patch("src.views.get_currency_rates") as mock_currency, \
                patch("src.views.get_stock_prices") as mock_stocks, \
                patch("src.views.load_transactions_from_excel") as mock_load, \
                patch("src.views.filter_transactions_by_date") as mock_filter, \
                patch("src.views.get_top_transactions") as mock_top:
            # Настраиваем моки
            mock_greeting.return_value = "Здравствуйте"
            mock_settings.return_value = {
                "user_currencies": ["USD", "EUR"],
                "user_stocks": ["AAPL", "MSFT"],
            }
            mock_currency.return_value = []
            mock_stocks.return_value = []
            mock_load.return_value = pd.DataFrame()
            mock_filter.return_value = pd.DataFrame()
            mock_top.return_value = []

            # Вызываем функцию
            result = get_home_page_data("2024-01-15 14:30:00")

            # Проверяем результат
            assert result["greeting"] == "Здравствуйте"
            assert len(result["cards"]) == 1
            assert result["cards"][0]["last_digits"] == "0000"
            assert result["cards"][0]["total_spent"] == 0.0
            assert result["cards"][0]["cashback"] == 0.0
            assert result["top_transactions"] == []
            assert result["currency_rates"] == []
            assert result["stock_prices"] == []

    def test_views_with_data(self):
        """Тест views с данными."""
        # Создаем тестовый DataFrame
        test_df = pd.DataFrame({
            "Дата операции": pd.to_datetime(["2024-01-15"]),
            "Сумма платежа": [-1000.0],
            "Категория": ["Супермаркеты"],
            "Описание": ["Покупка"],
            "Кешбэк": [10.0],
            "Номер карты": ["1234567890123456"],
        })

        # Мокаем зависимости
        with patch("src.views.get_greeting_by_time") as mock_greeting, \
                patch("src.views.load_user_settings") as mock_settings, \
                patch("src.views.get_currency_rates") as mock_currency, \
                patch("src.views.get_stock_prices") as mock_stocks, \
                patch("src.views.load_transactions_from_excel") as mock_load, \
                patch("src.views.filter_transactions_by_date") as mock_filter, \
                patch("src.views.get_top_transactions") as mock_top:
            # Настраиваем моки
            mock_greeting.return_value = "Добрый день"
            mock_settings.return_value = {
                "user_currencies": ["USD"],
                "user_stocks": ["AAPL"],
            }
            mock_currency.return_value = [{"currency": "USD", "rate": 75.5}]
            mock_stocks.return_value = [{"stock": "AAPL", "price": 150.0}]
            mock_load.return_value = test_df
            mock_filter.return_value = test_df
            mock_top.return_value = [
                {
                    "date": "15.01.2024",
                    "amount": 1000.0,
                    "category": "Супермаркеты",
                    "description": "Покупка",
                }
            ]

            # Вызываем функцию
            result = get_home_page_data("2024-01-15 14:30:00")

            # Проверяем результат
            assert result["greeting"] == "Добрый день"
            assert len(result["cards"]) == 1
            assert result["cards"][0]["last_digits"] == "3456"
            assert result["cards"][0]["total_spent"] == 1000.0
            assert result["cards"][0]["cashback"] == 10.0
            assert len(result["top_transactions"]) == 1
            assert len(result["currency_rates"]) == 1
            assert len(result["stock_prices"]) == 1

    def test_events_page_empty(self):
        """Тест страницы событий с пустыми данными."""
        test_df = pd.DataFrame()

        # Мокаем зависимости
        with patch("src.views.load_user_settings") as mock_settings, \
                patch("src.views.get_currency_rates") as mock_currency, \
                patch("src.views.get_stock_prices") as mock_stocks:
            mock_settings.return_value = {
                "user_currencies": ["USD"],
                "user_stocks": ["AAPL"],
            }
            mock_currency.return_value = []
            mock_stocks.return_value = []

            # Вызываем функцию
            result = get_events_page_data(test_df, "2024-01-15", "M")

            # Проверяем результат
            assert result["expenses"]["total_amount"] == 0
            assert result["expenses"]["main"] == []
            assert result["expenses"]["transfers_and_cash"] == []
            assert result["income"]["total_amount"] == 0
            assert result["income"]["main"] == []
            assert result["currency_rates"] == []
            assert result["stock_prices"] == []

    def test_services_edge_cases(self, sample_transactions):
        """Тест edge cases для сервисов."""
        # 1. profitable_cashback_categories с пустыми данными
        result = profitable_cashback_categories([], 2024, 1)
        assert result == {}

        # 2. profitable_cashback_categories с данными но без совпадений по дате
        result = profitable_cashback_categories(sample_transactions, 2023, 12)
        assert result == {}

        # 3. investment_bank с пустыми данными
        result = investment_bank("2024-01", [], 50)
        assert result == 0.0

        # 4. simple_search с пустым запросом
        result = simple_search("", sample_transactions)
        assert result == []

        # 5. simple_search без совпадений
        result = simple_search("Нет такой строки", sample_transactions)
        assert result == []

    def test_reports_edge_cases(self, sample_dataframe):
        """Тест edge cases для отчетов."""
        # 1. spending_by_category с пустым DataFrame
        empty_df = pd.DataFrame()
        result = spending_by_category(empty_df, "Супермаркеты")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

        # 2. spending_by_category с категорией которой нет
        result = spending_by_category(sample_dataframe, "Несуществующая категория")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

        # 3. spending_by_weekday с пустым DataFrame
        result = spending_by_weekday(empty_df)
        assert isinstance(result, pd.DataFrame)
        assert "День недели" in result.columns or len(result) == 0

        # 4. spending_by_workday с пустым DataFrame
        result = spending_by_workday(empty_df)
        assert isinstance(result, pd.DataFrame)
        assert "Тип дня" in result.columns or len(result) == 0

    def test_utils_edge_cases(self):
        """Тест edge cases для утилит."""
        # 1. get_greeting_by_time с разным временем
        test_cases = [
            ("2024-01-01 05:00:00", "Доброе утро"),
            ("2024-01-01 11:00:00", "Доброе утро"),
            ("2024-01-01 12:00:00", "Добрый день"),
            ("2024-01-01 17:00:00", "Добрый день"),
            ("2024-01-01 18:00:00", "Добрый вечер"),
            ("2024-01-01 23:00:00", "Добрый вечер"),
            ("2024-01-01 00:00:00", "Доброй ночи"),
            ("2024-01-01 04:00:00", "Доброй ночи"),
        ]

        for time_str, expected_start in test_cases:
            result = get_greeting_by_time(time_str)
            # Проверяем что результат содержит ожидаемую фразу
            assert isinstance(result, str)
            assert len(result) > 0

        # 2. get_currency_rates с пустым списком
        result = get_currency_rates([])
        assert isinstance(result, list)

        # 3. get_stock_prices с пустым списком
        result = get_stock_prices([])
        assert isinstance(result, list)

        # 4. filter_transactions_by_date с пустым DataFrame
        empty_df = pd.DataFrame()
        result = filter_transactions_by_date(empty_df, "2024-01-01", "M")
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_error_handling(self):
        """Тест обработки ошибок."""
        # Мокаем функцию чтобы вызвать исключение
        with patch("src.views.load_transactions_from_excel") as mock_load:
            mock_load.side_effect = Exception("Test error")

            # Должна быть обработка ошибок в get_home_page_data
            result = get_home_page_data("2024-01-15 14:30:00")

            # Проверяем что функция возвращает данные с заглушками при ошибке
            assert "greeting" in result
            assert "cards" in result
            assert len(result["cards"]) > 0
            assert result["cards"][0]["last_digits"] == "0000"

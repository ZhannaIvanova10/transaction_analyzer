"""
Тесты для views.
"""
import logging
from datetime import datetime

import pandas as pd
import pytest

from src.views import get_events_page_data, get_home_page_data


class TestViews:
    """Тесты для views."""

    def test_get_home_page_data_success(self):
        """Тест успешного получения данных главной страницы."""
        date_str = "2024-01-15 14:30:00"
        result = get_home_page_data(date_str)

        assert "greeting" in result
        assert "cards" in result
        assert "top_transactions" in result
        assert "currency_rates" in result
        assert "stock_prices" in result
        assert "current_date" in result

        # Проверяем структуру данных
        assert isinstance(result["greeting"], str)
        assert isinstance(result["cards"], list)
        assert isinstance(result["top_transactions"], list)
        assert isinstance(result["currency_rates"], list)
        assert isinstance(result["stock_prices"], list)

        # Проверяем что greeting соответствует времени
        # 14:30 - это день
        assert result["greeting"] == "Добрый день"

    def test_get_home_page_data_invalid_date(self):
        """Тест получения данных с невалидной датой."""
        date_str = "invalid-date"
        result = get_home_page_data(date_str)

        # При невалидной дате должно вернуться "Здравствуйте"
        assert result["greeting"] == "Здравствуйте"
        assert "cards" in result
        assert "top_transactions" in result

    def test_get_events_page_data_monthly(self):
        """Тест получения данных за месяц."""
        # Создаем тестовый DataFrame
        df = pd.DataFrame({
            "Дата операции": [
                "2024-01-15", "2024-01-16", "2024-02-01",
                "2024-01-17", "2023-12-31"  # Другой месяц/год
            ],
            "Сумма платежа": [-1000, -500, 2000, -300, -100],
            "Категория": ["Супермаркеты", "Кафе", "Зарплата", "Транспорт", "Супермаркеты"],
            "Номер карты": ["****1234", "****1234", "****5678", "****1234", "****1234"]
        })

        date_str = "2024-01-20"
        result = get_events_page_data(df, date_str, "M")

        # Должны быть только январские транзакции
        # -1000 (Супермаркеты), -500 (Кафе), 2000 (Зарплата), -300 (Транспорт)
        assert "expenses" in result
        assert "income" in result
        assert "currency_rates" in result
        assert "stock_prices" in result

        # Сумма расходов: 1000 + 500 + 300 = 1800
        assert result["expenses"]["total_amount"] == 1800

        # Сумма доходов: 2000
        assert result["income"]["total_amount"] == 2000

    def test_get_events_page_data_empty_dataframe(self):
        """Тест получения данных с пустым DataFrame."""
        empty_df = pd.DataFrame()
        date_str = "2024-01-15"
        result = get_events_page_data(empty_df, date_str)

        assert "expenses" in result
        assert "income" in result

        # При пустых данных должны быть нули
        assert result["expenses"]["total_amount"] == 0
        assert result["income"]["total_amount"] == 0

    def test_get_events_page_data_missing_columns(self):
        """Тест получения данных без необходимых колонок."""
        df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
        date_str = "2024-01-15"
        result = get_events_page_data(df, date_str)

        assert "expenses" in result
        assert "income" in result

        # При отсутствии колонок должны быть нули
        assert result["expenses"]["total_amount"] == 0
        assert result["income"]["total_amount"] == 0

    @pytest.mark.parametrize("period", ["W", "M", "Y", "ALL"])
    def test_get_events_page_data_all_periods(self, period):
        """Тест получения данных за все периоды."""
        df = pd.DataFrame({
            "Дата операции": ["2024-01-15", "2024-01-16"],
            "Сумма платежа": [-1000, -500],
            "Категория": ["Супермаркеты", "Кафе"],
            "Номер карты": ["****1234", "****1234"]
        })

        date_str = "2024-01-20"
        result = get_events_page_data(df, date_str, period)

        assert "expenses" in result
        assert "income" in result
        assert isinstance(result["expenses"]["total_amount"], int)

    def test_get_events_page_data_invalid_period(self):
        """Тест получения данных с невалидным периодом."""
        df = pd.DataFrame({
            "Дата операции": ["2024-01-15"],
            "Сумма платежа": [-1000],
            "Категория": ["Супермаркеты"],
        })

        date_str = "2024-01-20"
        result = get_events_page_data(df, date_str, "INVALID")

        # При невалидном периоде должна использоваться месячная фильтрация
        assert "expenses" in result
        assert result["expenses"]["total_amount"] == 1000

    def test_views_logging(self, caplog):
        """Тест логирования в views."""
        with caplog.at_level(logging.INFO):
            get_home_page_data("2024-01-15 14:30:00")

        assert "Сгенерированы данные главной страницы" in caplog.text

    def test_get_events_page_data_week_period(self):
        """Тест получения данных за неделю."""
        df = pd.DataFrame({
            "Дата операции": [
                "2024-01-15",  # Понедельник недели 15-21 января
                "2024-01-16",  # Вторник
                "2024-01-22",  # Следующий понедельник
            ],
            "Сумма платежа": [-1000, -500, -300],
            "Категория": ["Супермаркеты", "Кафе", "Транспорт"],
        })

        date_str = "2024-01-18"  # Четверг недели 15-21 января
        result = get_events_page_data(df, date_str, "W")

        # Должны быть только транзакции за неделю 15-21 января
        assert result["expenses"]["total_amount"] == 1500  # 1000 + 500

    def test_get_events_page_data_year_period(self):
        """Тест получения данных за год."""
        df = pd.DataFrame({
            "Дата операции": [
                "2024-01-15",
                "2024-06-01",
                "2023-12-31",  # Прошлый год
            ],
            "Сумма платежа": [-1000, -500, -300],
            "Категория": ["Супермаркеты", "Кафе", "Транспорт"],
        })

        date_str = "2024-07-01"
        result = get_events_page_data(df, date_str, "Y")

        # Должны быть только транзакции за 2024 год
        assert result["expenses"]["total_amount"] == 1500  # 1000 + 500

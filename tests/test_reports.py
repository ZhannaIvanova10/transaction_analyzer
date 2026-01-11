"""
Тесты для модуля reports.py
"""

import json
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

import pandas as pd
import pytest

from src.reports import (spending_by_category, spending_by_weekday,
                         spending_by_workday)


class TestReports:
    """Тесты для функций отчетов."""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)  # Уменьшим период для тестов

        dates = pd.date_range(start_date, end_date, freq="D")

        return pd.DataFrame(
            {
                "Дата операции": dates,
                "Сумма платежа": [-100 * (i % 10 + 1) for i in range(len(dates))],
                "Категория": ["Супермаркеты" if i % 3 == 0 else "Кафе" for i in range(len(dates))],
            }
        )

    def test_spending_by_category_with_data(self, sample_transactions):
        """Тест анализа трат по категории с данными."""
        result = spending_by_category(sample_transactions, "Супермаркеты")
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert "Месяц" in result.columns
            assert "Сумма расходов" in result.columns

    def test_spending_by_category_no_data(self, sample_transactions):
        """Тест анализа трат по несуществующей категории."""
        result = spending_by_category(sample_transactions, "Несуществующая категория")
        assert isinstance(result, pd.DataFrame)

    def test_spending_by_weekday(self, sample_transactions):
        """Тест анализа трат по дням недели."""
        result = spending_by_weekday(sample_transactions)
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert "День недели" in result.columns
            assert "Средние траты" in result.columns

    def test_spending_by_workday(self, sample_transactions):
        """Тест анализа трат по типам дней."""
        result = spending_by_workday(sample_transactions)
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert "Тип дня" in result.columns
            assert "Средние траты" in result.columns

    def test_spending_by_category_with_specific_date(self, sample_transactions):
        """Тест анализа трат по категории с указанной датой."""
        test_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        result = spending_by_category(sample_transactions, "Супермаркеты", test_date)
        assert isinstance(result, pd.DataFrame)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_report_decorator(self, mock_json_dump, mock_file, sample_transactions):
        """Тест работы декоратора отчетов."""
        result = spending_by_category(sample_transactions, "Супермаркеты")
        mock_file.assert_called()
        # Декоратор всегда пытается записать результат
        assert mock_json_dump.called

    def test_invalid_date_format(self, sample_transactions):
        """Тест обработки неверного формата даты."""
        result = spending_by_category(sample_transactions, "Супермаркеты", "неверная-дата")
        assert isinstance(result, pd.DataFrame)
        # При неверном формате даты должна вернуться пустая DataFrame
        assert result.empty

    def test_spending_by_category_with_empty_dataframe(self):
        """Тест анализа с пустым DataFrame."""
        empty_df = pd.DataFrame()
        result = spending_by_category(empty_df, "Супермаркеты")
        assert result.empty

    def test_spending_by_weekday_with_empty_dataframe(self):
        """Тест анализа по дням недели с пустым DataFrame."""
        empty_df = pd.DataFrame()
        result = spending_by_weekday(empty_df)
        assert result.empty

    def test_spending_by_workday_with_empty_dataframe(self):
        """Тест анализа по типам дней с пустым DataFrame."""
        empty_df = pd.DataFrame()
        result = spending_by_workday(empty_df)
        assert result.empty

    @pytest.mark.parametrize("date_str", ["2024-01-15", "2024-02-28", "2024-12-31"])
    def test_spending_by_category_with_different_dates(self, sample_transactions, date_str):
        """Тест анализа трат по категории с разными датами."""
        result = spending_by_category(sample_transactions, "Супермаркеты", date_str)
        assert isinstance(result, pd.DataFrame)

    def test_spending_by_category_missing_columns(self):
        """Тест анализа при отсутствии необходимых колонок."""
        df = pd.DataFrame({"Дата": [datetime.now()], "Сумма": [-100], "Кат": ["Супермаркеты"]})
        result = spending_by_category(df, "Супермаркеты")
        assert result.empty

    @patch("src.reports.logger")
    def test_spending_by_category_logging(self, mock_logger, sample_transactions):
        """Тест логирования в функции анализа трат по категории."""
        result = spending_by_category(sample_transactions, "Супермаркеты")
        # Проверяем, что logger вызывался
        assert mock_logger.info.called or mock_logger.warning.called

    def test_spending_by_category_positive_amounts(self):
        """Тест анализа с положительными суммами."""
        df = pd.DataFrame(
            {
                "Дата операции": [datetime.now()],
                "Сумма платежа": [100],  # Положительная сумма
                "Категория": ["Супермаркеты"],
            }
        )
        result = spending_by_category(df, "Супермаркеты")
        assert isinstance(result, pd.DataFrame)

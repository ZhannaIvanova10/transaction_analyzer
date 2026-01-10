"""
Тесты для модуля reports.py
"""
import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open

from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday
)


class TestReports:
    """Тесты для функций отчетов."""
    
    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = pd.date_range(start_date, end_date, freq='D')
        
        return pd.DataFrame({
            'Дата операции': dates,
            'Сумма платежа': [-100 * (i % 10 + 1) for i in range(len(dates))],
            'Категория': ['Супермаркеты' if i % 3 == 0 else 'Кафе' for i in range(len(dates))]
        })
    
    def test_spending_by_category_with_data(self, sample_transactions):
        """Тест анализа трат по категории с данными."""
        result = spending_by_category(sample_transactions, "Супермаркеты")
        
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert 'Месяц' in result.columns
            assert 'Сумма расходов' in result.columns
    def test_spending_by_category_no_data(self, sample_transactions):
        """Тест анализа трат по несуществующей категории."""
        result = spending_by_category(sample_transactions, "Несуществующая категория")
        
        assert isinstance(result, pd.DataFrame)
        assert result.empty
    
    def test_spending_by_weekday(self, sample_transactions):
        """Тест анализа трат по дням недели."""
        result = spending_by_weekday(sample_transactions)
        
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert 'День недели' in result.columns
            assert 'Средние траты' in result.columns
    
    def test_spending_by_workday(self, sample_transactions):
        """Тест анализа трат по типам дней."""
        result = spending_by_workday(sample_transactions)
        assert isinstance(result, pd.DataFrame)
        if not result.empty:
            assert 'Тип дня' in result.columns
            assert 'Средние траты' in result.columns
    
    def test_spending_by_category_with_specific_date(self, sample_transactions):
        """Тест анализа трат по категории с указанной датой."""
        test_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        result = spending_by_category(sample_transactions, "Супермаркеты", test_date)
        
        assert isinstance(result, pd.DataFrame)
    
    @patch("builtins.open", new_callable=mock_open)
    def test_report_decorator(self, mock_file, sample_transactions):
        """Тест работы декоратора отчетов."""
        # Мокаем json.dump чтобы проверить, что он вызывается
        with patch('json.dump') as mock_json_dump:
            result = spending_by_category(sample_transactions, "Супермаркеты")
            # Проверяем, что файл был открыт для записи
            mock_file.assert_called()
            
            # Проверяем, что json.dump был вызван
            if not result.empty:
                mock_json_dump.assert_called()
    
    def test_invalid_date_format(self, sample_transactions):
        """Тест обработки неверного формата даты."""
        with pytest.raises(ValueError):
            spending_by_category(sample_transactions, "Супермаркеты", "неверная-дата")

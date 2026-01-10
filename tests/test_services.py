"""
Тесты для модуля services.py
"""
import pytest
from datetime import datetime
from src.services import (
    profitable_cashback_categories,
    investment_bank,
    simple_search,
    search_by_phone_numbers,
    search_by_person_transfers
)


class TestServices:
    """Тесты для сервисов."""
    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        return [
            {
                "Дата операции": "2024-01-15",
                "Категория": "Супермаркеты",
                "Сумма операции": 1000,
                "Кешбэк": 10
            },
            {
                "Дата операции": "2024-01-20",
                "Категория": "Кафе",
                "Сумма операции": 500,
                "Кешбэк": 5
            },
            {
                "Дата операции": "2024-02-10",
                "Категория": "Супермаркеты",
                "Сумма операции": 1500,
                "Кешбэк": 15
            }
        ]
    def test_profitable_cashback_categories(self, sample_transactions):
        """Тест анализа выгодных категорий кешбэка."""
        result = profitable_cashback_categories(sample_transactions, 2024, 1)
        
        assert "Супермаркеты" in result
        assert "Кафе" in result
        assert result["Супермаркеты"] > 0
    
    def test_investment_bank(self):
        """Тест расчета инвесткопилки."""
        transactions = [
            {"Дата операции": "2024-01-15", "Сумма операции": 1712},
            {"Дата операции": "2024-01-16", "Сумма операции": 845},
            {"Дата операции": "2024-02-01", "Сумма операции": 1200}  # Другой месяц
        ]
        
        result = investment_bank("2024-01", transactions, 50)
        
        # 1712 округляется до 1750 (+38)
        # 845 округляется до 850 (+5)
        # 1200 игнорируется (другой месяц)
        assert result == 43.0
    def test_simple_search_found(self):
        """Тест успешного поиска транзакций."""
        transactions = [
            {"Описание": "Оплата в супермаркете", "Категория": "Супермаркеты"},
            {"Описание": "Обед в кафе", "Категория": "Кафе"},
            {"Описание": "Такси домой", "Категория": "Транспорт"}
        ]
        
        result = simple_search("кафе", transactions)
        
        assert len(result) == 1
        assert result[0]["Категория"] == "Кафе"
    
    def test_simple_search_not_found(self):
        """Тест поиска без результатов."""
        transactions = [
            {"Описание": "Оплата в супермаркете", "Категория": "Супермаркеты"}
        ]
        
        result = simple_search("ресторан", transactions)
        
        assert len(result) == 0
    def test_search_by_phone_numbers(self):
        """Тест поиска по телефонным номерам."""
        transactions = [
            {"Описание": "Оплата услуг +7 921 123-45-67"},
            {"Описание": "Перевод на карту"},
            {"Описание": "Мобильная связь +79995556677"}
        ]
        
        result = search_by_phone_numbers(transactions)
        
        assert len(result) == 2
    
    def test_search_by_person_transfers(self):
        """Тест поиска переводов физическим лицам."""
        transactions = [
            {"Категория": "Переводы", "Описание": "Перевод Ивану И."},
            {"Категория": "Переводы", "Описание": "Пополнение счета"},
            {"Категория": "Супермаркеты", "Описание": "Петр П."}
        ]
        result = search_by_person_transfers(transactions)
        
        assert len(result) == 1
        assert result[0]["Описание"] == "Перевод Ивану И."

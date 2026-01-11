"""
Тесты для модуля services.py.
"""

import re
from datetime import datetime

import pytest

from src.services import (investment_bank, profitable_cashback_categories,
                          search_by_person_transfers, search_by_phone_numbers,
                          simple_search)


class TestServices:
    """Тесты для services.py."""

    @pytest.fixture
    def sample_transactions(self):
        """Фикстура с тестовыми транзакциями."""
        return [
            {
                "Дата операции": "2024-01-15",
                "Сумма операции": 1000.0,
                "Категория": "Супермаркеты",
                "Описание": "Покупка в магазине",
                "Кешбэк": 10.0,
            },
            {
                "Дата операции": "2024-01-10",
                "Сумма операции": 500.0,
                "Категория": "Рестораны",
                "Описание": "Ужин в кафе +7 999 123-45-67",
                "Кешбэк": 5.0,
            },
            {
                "Дата операции": "2024-01-05",
                "Сумма операции": 2000.0,
                "Категория": "Переводы",
                "Описание": "Перевод Иван С.",
                "Кешбэк": 0.0,
            },
        ]
    def test_profitable_cashback_categories(self, sample_transactions):
        """Тест анализа выгодных категорий кешбэка."""
        result = profitable_cashback_categories(sample_transactions, 2024, 1)

        assert isinstance(result, dict)
        assert "Супермаркеты" in result
        assert "Рестораны" in result
        assert result["Супермаркеты"] == 10.0
        assert result["Рестораны"] == 5.0

    def test_profitable_cashback_categories_no_data(self):
        """Тест анализа кешбэка без данных."""
        result = profitable_cashback_categories([], 2024, 1)
        assert result == {}

    def test_investment_bank(self, sample_transactions):
        """Тест расчета Инвесткопилки."""
        result = investment_bank("2024-01", sample_transactions, 50)

        assert isinstance(result, float)
        assert result >= 0

    def test_investment_bank_no_transactions(self):
        """Тест расчета Инвесткопилки без транзакций."""
        result = investment_bank("2024-01", [], 50)
        assert result == 0.0
    def test_simple_search_found(self, sample_transactions):
        """Тест простого поиска - найдено."""
        result = simple_search("магазин", sample_transactions)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["Категория"] == "Супермаркеты"

    def test_simple_search_not_found(self, sample_transactions):
        """Тест простого поиска - не найдено."""
        result = simple_search("несуществующий запрос", sample_transactions)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_simple_search_empty_query(self, sample_transactions):
        """Тест простого поиска с пустым запросом."""
        result = simple_search("", sample_transactions)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_by_phone_numbers(self, sample_transactions):
        """Тест поиска по телефонным номерам."""
        result = search_by_phone_numbers(sample_transactions)
        assert isinstance(result, list)
        assert len(result) == 1
        assert "+7 999 123-45-67" in result[0]["Описание"]

    def test_search_by_phone_numbers_no_phones(self):
        """Тест поиска по телефонным номерам без номеров."""
        transactions = [
            {"Описание": "Покупка без номера"},
            {"Описание": "Еще одна покупка"},
        ]
        result = search_by_phone_numbers(transactions)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_by_person_transfers(self, sample_transactions):
        """Тест поиска переводов физлицам."""
        result = search_by_person_transfers(sample_transactions)

        assert isinstance(result, list)
        assert len(result) == 1
        assert "Иван С." in result[0]["Описание"]

    def test_search_by_person_transfers_no_transfers(self):
        """Тест поиска переводов физлицам без переводов."""
        transactions = [
            {"Категория": "Супермаркеты", "Описание": "Покупка"},
            {"Категория": "Рестораны", "Описание": "Ужин"},
        ]
        result = search_by_person_transfers(transactions)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_phone_regex_pattern(self):
        """Тест регулярного выражения для номеров телефонов."""
        phone_pattern = re.compile(
            r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'
        )

        test_cases = [
            ("+7 999 123-45-67", True),
            ("8(999)123-45-67", True),
            ("89991234567", True),
            ("+7(999)1234567", True),
            ("7 999 123 45 67", False),  # без +7 или 8
            ("test", False),
            ("", False),
        ]

        for phone, expected in test_cases:
            assert bool(phone_pattern.search(phone)) == expected

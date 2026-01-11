"""
Тесты для сервисов.
"""
import logging
import re
from datetime import datetime

import pandas as pd
import pytest

from src.services import (
    investment_bank,
    profitable_cashback_categories,
    search_by_person_transfers,
    search_by_phone_numbers,
    simple_search,
)


class TestServices:
    """Тесты для сервисов."""

    def test_profitable_cashback_categories(self):
        """Тест выгодных категорий кешбэка."""
        transactions = [
            {
                "Дата операции": "2024-01-15",
                "Сумма платежа": -1000,
                "Категория": "Супермаркеты",
                "Кешбэк": 10.0
            },
            {
                "Дата операции": "2024-01-16",
                "Сумма платежа": -500,
                "Категория": "Кафе",
                "Кешбэк": 5.0
            },
            {
                "Дата операции": "2024-01-17",
                "Сумма платежа": -2000,
                "Категория": "Супермаркеты",
                "Кешбэк": 20.0
            },
        ]

        result = profitable_cashback_categories(transactions, 2024, 1)

        assert "Супермаркеты" in result
        assert "Кафе" in result
        assert result["Супермаркеты"] == 30.0
        assert result["Кафе"] == 5.0

    def test_profitable_cashback_categories_no_data(self):
        """Тест выгодных категорий без данных."""
        result = profitable_cashback_categories([], 2024, 1)
        assert result == {}

    def test_investment_bank(self):
        """Тест расчета инвесткопилки."""
        transactions = [
            {
                "Дата операции": "2024-01-15",
                "Сумма операции": -1712,
                "Округление на «Инвесткопилку»": 38.0
            },
            {
                "Дата операции": "2024-01-16",
                "Сумма операции": -845,
                "Округление на «Инвесткопилку»": 5.0
            },
            {
                "Дата операции": "2024-02-01",
                "Сумма операции": -1200,
                "Округление на «Инвесткопилку»": 0.0
            },
        ]

        result = investment_bank("2024-01", transactions, 50)
        # 38 + 5 = 43
        assert result == 43.0

    def test_investment_bank_no_transactions(self):
        """Тест инвесткопилки без транзакций."""
        result = investment_bank("2024-01", [], 50)
        assert result == 0.0

    def test_simple_search_found(self):
        """Тест успешного поиска транзакций."""
        transactions = [
            {"Описание": "Оплата в супермаркете", "Категория": "Супермаркеты"},
            {"Описание": "Обед в кафе", "Категория": "Кафе"},
            {"Описание": "Такси домой", "Категория": "Транспорт"},
        ]

        result = simple_search("кафе", transactions)
        assert len(result) == 1
        assert result[0]["Категория"] == "Кафе"

    def test_simple_search_not_found(self):
        """Тест поиска без результатов."""
        transactions = [
            {"Описание": "Оплата в супермаркете", "Категория": "Супермаркеты"},
            {"Описание": "Обед в кафе", "Категория": "Кафе"},
        ]

        result = simple_search("ресторан", transactions)
        assert len(result) == 0

    def test_simple_search_empty_query(self):
        """Тест поиска с пустым запросом."""
        transactions = [
            {"Описание": "Оплата в супермаркете", "Категория": "Супермаркеты"},
        ]

        result = simple_search("", transactions)
        assert len(result) == 0

    def test_search_by_phone_numbers(self):
        """Тест поиска по телефонным номерам."""
        transactions = [
            {"Описание": "Пополнение +7 921 111-22-33"},
            {"Описание": "Перевод на карту 8(999)123-45-67"},
            {"Описание": "Оплата услуг"},
        ]

        result = search_by_phone_numbers(transactions)
        assert len(result) == 2
        assert "+7 921 111-22-33" in result[0]["Описание"] or "8(999)123-45-67" in result[0]["Описание"]

    def test_search_by_phone_numbers_no_phones(self):
        """Тест поиска телефонных номеров без результатов."""
        transactions = [
            {"Описание": "Оплата в супермаркете"},
            {"Описание": "Пополнение счета"},
        ]

        result = search_by_phone_numbers(transactions)
        assert len(result) == 0

    def test_search_by_person_transfers(self):
        """Тест поиска переводов физическим лицам."""
        transactions = [
            {"Категория": "Переводы", "Описание": "Иван П."},
            {"Категория": "Переводы", "Описание": "Мария С."},
            {"Категория": "Супермаркеты", "Описание": "Петр В."},
        ]

        result = search_by_person_transfers(transactions)
        assert len(result) == 2
        assert result[0]["Категория"] == "Переводы"
        assert result[1]["Категория"] == "Переводы"

    def test_search_by_person_transfers_no_transfers(self):
        """Тест поиска переводов без результатов."""
        transactions = [
            {"Категория": "Супермаркеты", "Описание": "Иван П."},
            {"Категория": "Кафе", "Описание": "Мария С."},
        ]

        result = search_by_person_transfers(transactions)
        assert len(result) == 0

    def test_services_logging(self, caplog):
        """Тест логирования в сервисах."""
        with caplog.at_level(logging.WARNING):
            result = profitable_cashback_categories([], 2024, 1)

        assert "Нет данных для анализа кешбэка" in caplog.text

    def test_phone_regex_pattern(self):
        """Тест регулярного выражения для телефонов."""
        phone_pattern = r'(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}'

        valid_numbers = [
            "+7 921 111-22-33",
            "8(921)111-22-33",
            "+79211112233",
            "8 921 111 22 33",
        ]

        invalid_numbers = [
            "921-111-22-33",  # нет +7 или 8
            "+7921",  # слишком короткий
            "телефон",  # не номер
        ]

        for number in valid_numbers:
            assert re.search(phone_pattern, number) is not None, f"Failed: {number}"

        for number in invalid_numbers:
            assert re.search(phone_pattern, number) is None, f"Should fail: {number}"

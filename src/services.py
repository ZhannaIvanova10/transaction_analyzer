"""
Модуль с сервисами для анализа транзакций.
Используются элементы функционального программирования.
"""

import json
import logging
import re
from datetime import datetime
from functools import reduce
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def profitable_cashback_categories(
    transactions: List[Dict[str, Any]], year: int, month: int
) -> Dict[str, float]:
    """
    Анализирует выгодные категории повышенного кешбэка.

    Args:
        transactions: Список транзакций
        year: Год для анализа
        month: Месяц для анализа

    Returns:
        Словарь с категориями и суммами кешбэка
    """
    try:
        logger.info("Анализ выгодных категорий кешбэка за %d-%d", month, year)

        # Используем filter для фильтрации по дате (ФП)
        def filter_by_date(transaction: Dict[str, Any]) -> bool:
            """Фильтрует транзакции по году и месяцу."""
            try:
                date_str = transaction.get("Дата операции", "")
                if date_str:
                    trans_date = datetime.strptime(date_str, "%Y-%m-%d")
                    return trans_date.year == year and trans_date.month == month
            except (ValueError, KeyError):
                pass
            return False

        # Используем map и filter (ФП)
        filtered_transactions = list(filter(filter_by_date, transactions))

        if not filtered_transactions:
            logger.warning("Нет транзакций за указанный период")
            return {}

        # Используем lambda и map для извлечения кешбэка (ФП)
        def extract_cashback(transaction: Dict[str, Any]) -> float:
            """Извлекает сумму кешбэка из транзакции."""
            cashback = transaction.get("Кешбэк", 0)
            return float(cashback) if cashback else 0.0

        # Группируем по категориям с использованием reduce (ФП)
        def reducer(
            acc: Dict[str, float], transaction: Dict[str, Any]
        ) -> Dict[str, float]:
            """Аккумулятор для reduce."""
            category = transaction.get("Категория", "Без категории")
            cashback = extract_cashback(transaction)
            acc[category] = acc.get(category, 0.0) + cashback
            return acc

        # Исправляем type annotation для reduce
        initial_result: Dict[str, float] = {}
        result = reduce(reducer, filtered_transactions, initial_result)

        # Сортируем по убыванию кешбэка
        sorted_result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

        logger.info("Проанализировано %d категорий с кешбэком", len(sorted_result))
        return sorted_result

    except Exception as e:
        logger.error("Ошибка при анализе выгодных категорий кешбэка: %s", e)
        return {}


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int
) -> float:
    """
    Рассчитывает сумму для Инвесткопилки.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Лимит округления

    Returns:
        Сумма для Инвесткопилки
    """
    try:
        logger.info("Расчет Инвесткопилки за %s с лимитом %d", month, limit)

        # Фильтруем транзакции за указанный месяц (ФП)
        target_year, target_month = map(int, month.split("-"))

        def filter_by_month(transaction: Dict[str, Any]) -> bool:
            """Фильтрует транзакции по месяцу."""
            try:
                date_str = transaction.get("Дата операции", "")
                if date_str:
                    trans_date = datetime.strptime(date_str, "%Y-%m-%d")
                    return (
                        trans_date.year == target_year
                        and trans_date.month == target_month
                    )
            except (ValueError, KeyError):
                pass
            return False

        month_transactions = list(filter(filter_by_month, transactions))

        if not month_transactions:
            logger.warning("Нет транзакций за указанный месяц")
            return 0.0

        # Используем map и sum для расчета (ФП)
        def calculate_rounding(transaction: Dict[str, Any]) -> float:
            """Рассчитывает округление для одной транзакции."""
            amount = abs(float(transaction.get("Сумма операции", 0)))
            if amount <= 0:
                return 0.0

            # Округляем до ближайшего кратного limit
            rounded = ((amount + limit - 1) // limit) * limit
            return rounded - amount

        # List comprehension (ФП)
        roundings = [calculate_rounding(t) for t in month_transactions]
        total_rounding = sum(roundings)

        logger.info(
            "Рассчитана сумма для Инвесткопилки: %.2f из %d транзакций",
            total_rounding,
            len(month_transactions),
        )
        return total_rounding

    except Exception as e:
        logger.error("Ошибка при расчете Инвесткопилки: %s", e)
        return 0.0


def simple_search(
    query: str, transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Простой поиск по описанию или категории.

    Args:
        query: Строка для поиска
        transactions: Список транзакций

    Returns:
        Список найденных транзакций
    """
    try:
        logger.info("Поиск по запросу: '%s'", query)

        if not query.strip():
            logger.warning("Пустой запрос поиска")
            return []

        query_lower = query.lower()

        # Используем filter с lambda (ФП)
        def matches_query(transaction: Dict[str, Any]) -> bool:
            """Проверяет, соответствует ли транзакция запросу."""
            description = str(transaction.get("Описание", "")).lower()
            category = str(transaction.get("Категория", "")).lower()

            return query_lower in description or query_lower in category

        result = list(filter(matches_query, transactions))

        logger.info("Найдено %d транзакций по запросу '%s'", len(result), query)
        return result

    except Exception as e:
        logger.error("Ошибка при поиске: %s", e)
        return []


def search_by_phone_numbers(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Поиск транзакций с телефонными номерами в описании.

    Args:
        transactions: Список транзакций

    Returns:
        Список транзакций с телефонными номерами
    """
    try:
        logger.info("Поиск транзакций с телефонными номерами")

        # Регулярное выражение для российских номеров телефонов
        phone_pattern = re.compile(
            r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
        )

        # Используем filter с lambda и регулярным выражением (ФП)
        def has_phone_number(transaction: Dict[str, Any]) -> bool:
            """Проверяет, содержит ли описание номер телефона."""
            description = str(transaction.get("Описание", ""))
            return bool(phone_pattern.search(description))

        result = list(filter(has_phone_number, transactions))

        logger.info("Найдено %d транзакций с телефонными номерами", len(result))
        return result

    except Exception as e:
        logger.error("Ошибка при поиске телефонных номеров: %s", e)
        return []


def search_by_person_transfers(
    transactions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Поиск переводов физическим лицам.

    Args:
        transactions: Список транзакций

    Returns:
        Список транзакций с переводами физлицам
    """
    try:
        logger.info("Поиск переводов физическим лицам")

        # Регулярное выражение для имен с инициалами (Имя Ф.)
        name_pattern = re.compile(r"[А-ЯЁ][а-яё]+\s[А-ЯЁ]\.")

        # Используем filter с lambda (ФП)
        def is_person_transfer(transaction: Dict[str, Any]) -> bool:
            """Проверяет, является ли транзакция переводом физлицу."""
            category = str(transaction.get("Категория", "")).lower()
            description = str(transaction.get("Описание", ""))

            # Проверяем категорию "Переводы" и наличие имени с инициалами
            return "перевод" in category and bool(name_pattern.search(description))

        result = list(filter(is_person_transfer, transactions))

        logger.info("Найдено %d переводов физлицам", len(result))
        return result

    except Exception as e:
        logger.error("Ошибка при поиске переводов физлицам: %s", e)
        return []

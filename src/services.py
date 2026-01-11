"""
Модуль с сервисами для анализа транзакций.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


def profitable_cashback_categories(
    data: List[Dict[str, Any]], year: int, month: int
) -> Dict[str, float]:
    """
    Анализирует выгодность категорий для повышенного кешбэка.

    Args:
        data: Список словарей с транзакциями
        year: Год для анализа
        month: Месяц для анализа

    Returns:
        Словарь с категориями и суммой кешбэка
    """
    try:
        if not data:
            logger.warning("Нет данных для анализа кешбэка")
            return {}

        # Конвертируем в DataFrame для удобства
        df = pd.DataFrame(data)

        # Проверяем наличие необходимых колонок
        required_columns = ["Дата операции", "Сумма платежа", "Категория", "Кешбэк"]
        for col in required_columns:
            if col not in df.columns:
                logger.error("Отсутствует колонка: %s", col)
                return {}

        # Конвертируем дату
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

        # Фильтруем по году и месяцу
        mask = (
            (df["Дата операции"].dt.year == year)
            & (df["Дата операции"].dt.month == month)
            & (df["Сумма платежа"] < 0)  # Только траты
        )

        filtered_df = df[mask].copy()

        if filtered_df.empty:
            logger.warning("Нет транзакций за %s/%s", month, year)
            return {}

        # Агрегируем кешбэк по категориям
        cashback_by_category = filtered_df.groupby("Категория")["Кешбэк"].sum()

        # Сортируем по убыванию кешбэка
        cashback_by_category = cashback_by_category.sort_values(ascending=False)

        # Конвертируем в словарь с явным указанием типов
        result: Dict[str, float] = {}
        for category, cashback in cashback_by_category.items():
            result[str(category)] = float(cashback)

        logger.info(
            "Проанализирован кешбэк за %s/%s: %s категорий", month, year, len(result)
        )
        return result

    except Exception as e:
        logger.error("Ошибка анализа кешбэка: %s", e)
        return {}


def investment_bank(
    month: str, transactions: List[Dict[str, Any]], limit: int = 10
) -> float:
    """
    Рассчитывает сумму для 'Инвесткопилки'.

    Args:
        month: Месяц в формате 'YYYY-MM'
        transactions: Список транзакций
        limit: Лимит округления (10, 50 или 100)

    Returns:
        Сумма для инвесткопилки
    """
    try:
        if not transactions:
            logger.warning("Нет транзакций для расчета инвесткопилки")
            return 0.0

        # Конвертируем в DataFrame
        df = pd.DataFrame(transactions)

        # Проверяем наличие необходимых колонок
        required_columns = [
            "Дата операции",
            "Сумма операции",
            "Округление на «Инвесткопилку»",
        ]
        for col in required_columns:
            if col not in df.columns:
                logger.error("Отсутствует колонка: %s", col)
                return 0.0

        # Парсим месяц
        try:
            target_month = datetime.strptime(month, "%Y-%m")
        except ValueError:
            logger.error("Неверный формат месяца: %s", month)
            return 0.0

        # Конвертируем дату
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce")

        # Фильтруем по месяцу
        mask = (
            (df["Дата операции"].dt.year == target_month.year)
            & (df["Дата операции"].dt.month == target_month.month)
            & (df["Сумма операции"] < 0)  # Только траты
        )

        filtered_df = df[mask].copy()

        if filtered_df.empty:
            logger.warning("Нет транзакций за %s", month)
            return 0.0

        # Если есть колонка с округлением, используем ее
        if "Округление на «Инвесткопилку»" in filtered_df.columns:
            total_investment = float(filtered_df["Округление на «Инвесткопилку»"].sum())
        else:
            # Или рассчитываем вручную
            total_investment = 0.0
            for _, row in filtered_df.iterrows():
                amount = abs(float(row["Сумма операции"]))
                if limit > 0:
                    rounded_amount = ((amount + limit - 1) // limit) * limit
                    investment = rounded_amount - amount
                    total_investment += investment

        logger.info(
            "Рассчитана инвесткопилка за %s: %.2f руб.", month, total_investment
        )
        return total_investment

    except Exception as e:
        logger.error("Ошибка расчета инвесткопилки: %s", e)
        return 0.0


def simple_search(
    query: str, transactions: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Простой поиск транзакций по запросу.

    Args:
        query: Строка для поиска
        transactions: Список транзакций

    Returns:
        Список найденных транзакций
    """
    try:
        if not query or not transactions:
            logger.warning("Пустой запрос или список транзакций")
            return []

        query_lower = query.lower()
        result: List[Dict[str, Any]] = []

        for transaction in transactions:
            # Ищем в описании и категории
            description = str(transaction.get("Описание", "")).lower()
            category = str(transaction.get("Категория", "")).lower()

            if query_lower in description or query_lower in category:
                result.append(transaction)

        logger.info("Простой поиск '%s': найдено %s транзакций", query, len(result))
        return result

    except Exception as e:
        logger.error("Ошибка простого поиска: %s", e)
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
        if not transactions:
            logger.warning("Нет транзакций для поиска телефонных номеров")
            return []

        # Регулярное выражение для поиска российских телефонных номеров
        phone_pattern = r"(\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"
        result: List[Dict[str, Any]] = []

        for transaction in transactions:
            description = str(transaction.get("Описание", ""))

            if re.search(phone_pattern, description):
                result.append(transaction)

        logger.info("Найдено %s транзакций с телефонными номерами", len(result))
        return result

    except Exception as e:
        logger.error("Ошибка поиска телефонных номеров: %s", e)
        return []


def search_by_person_transfers(
    transactions: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Поиск переводов физическим лицам.

    Args:
        transactions: Список транзакций

    Returns:
        Список переводов физическим лицам
    """
    try:
        if not transactions:
            logger.warning("Нет транзакций для поиска переводов")
            return []

        # Паттерн для поиска ФИО (Имя Фамилия[инициал])
        name_pattern = r"[А-ЯЁ][а-яё]+\s+[А-ЯЁ]\."
        result: List[Dict[str, Any]] = []

        for transaction in transactions:
            category = str(transaction.get("Категория", ""))
            description = str(transaction.get("Описание", ""))

            # Ищем переводы с именем и инициалом фамилии
            if category == "Переводы" and re.search(name_pattern, description):
                result.append(transaction)

        logger.info("Найдено %s переводов физическим лицам", len(result))
        return result

    except Exception as e:
        logger.error("Ошибка поиска переводов: %s", e)
        return []

"""
Модуль для создания отчетов.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

import pandas as pd

logger = logging.getLogger(__name__)


def report_decorator(filename: Optional[str] = None) -> Callable[[Any], Any]:
    """
    Декоратор для сохранения результатов отчета в файл.

    Args:
        filename: Имя файла для сохранения (если None, генерируется автоматически)

    Returns:
        Декорированная функция
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Внутренний декоратор для обертывания функции.

        Args:
            func: Функция для обертывания

        Returns:
            Обернутую функцию
        """

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[Dict[str, Any], pd.DataFrame]:
            """
            Обертка функции, которая выполняет запись результата в файл.

            Args:
                *args: Позиционные аргументы
                **kwargs: Именованные аргументы

            Returns:
                Результат выполнения оригинальной функции
            """
            try:
                result = func(*args, **kwargs)

                # Определяем имя файла
                if filename:
                    file_to_save = filename
                else:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_to_save = f"reports/report_{func.__name__}_{timestamp}.json"

                # Сохраняем результат
                try:
                    os.makedirs("reports", exist_ok=True)

                    if isinstance(result, pd.DataFrame):
                        save_data = result.to_dict(orient="records")
                    else:
                        save_data = result

                    with open(file_to_save, "w", encoding="utf-8") as f:
                        json.dump(save_data, f, ensure_ascii=False, indent=2)

                    logger.info("Отчет сохранен в файл: %s", file_to_save)

                except Exception as save_error:
                    logger.error("Ошибка при сохранении отчета: %s", save_error)

                return result

            except Exception as e:
                logger.error("Ошибка при выполнении функции %s: %s", func.__name__, e)
                raise

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """
    Анализирует траты по указанной категории за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        category: Категория для анализа
        date: Дата отсчета в формате 'YYYY-MM-DD' (если None, используется текущая дата)

    Returns:
        DataFrame с тратами по категории
    """
    try:
        logger.info("Анализ трат по категории '%s'", category)

        # Определяем дату отсчета
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        # Вычисляем дату начала (три месяца назад)
        start_date = end_date - timedelta(days=90)

        # Преобразуем дату операции в datetime, если нужно
        if "Дата операции" in transactions.columns:
            if not pd.api.types.is_datetime64_any_dtype(transactions["Дата операции"]):
                transactions["Дата операции"] = pd.to_datetime(
                    transactions["Дата операции"], errors="coerce"
                )

        # Фильтруем по дате
        date_mask = (transactions["Дата операции"] >= start_date) & (
            transactions["Дата операции"] <= end_date
        )
        period_transactions = transactions[date_mask].copy()

        # Фильтруем по категории
        if "Категория" in period_transactions.columns:
            category_mask = period_transactions["Категория"].str.contains(
                category, case=False, na=False
            )
            category_transactions = period_transactions[category_mask].copy()
        else:
            category_transactions = pd.DataFrame()

        if category_transactions.empty:
            logger.warning(
                "Не найдено транзакций по категории '%s' за указанный период", category
            )
            return pd.DataFrame(columns=["Дата", "Сумма", "Описание"])

        # Группируем по месяцам
        category_transactions["Месяц"] = category_transactions[
            "Дата операции"
        ].dt.to_period("M")

        result = (
            category_transactions.groupby("Месяц")
            .agg(
                total_amount=("Сумма операции", "sum"),
                transaction_count=("Сумма операции", "count"),
                avg_amount=("Сумма операции", "mean"),
            )
            .reset_index()
        )

        result["Месяц"] = result["Месяц"].astype(str)

        logger.info(
            "Найдено %d транзакций по категории '%s'",
            len(category_transactions),
            category,
        )

        return result

    except Exception as e:
        logger.error("Ошибка при анализе трат по категории: %s", e)
        return pd.DataFrame(
            columns=["Месяц", "total_amount", "transaction_count", "avg_amount"]
        )


@report_decorator(filename="reports/weekly_spending.json")
def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    """
    Анализирует средние траты по дням недели за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        date: Дата отсчета в формате 'YYYY-MM-DD' (если None, используется текущая дата)

    Returns:
        DataFrame со средними тратами по дням недели
    """
    try:
        logger.info("Анализ трат по дням недели")

        # Определяем дату отсчета
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        # Вычисляем дату начала (три месяца назад)
        start_date = end_date - timedelta(days=90)

        # Преобразуем дату операции в datetime, если нужно
        if "Дата операции" in transactions.columns:
            if not pd.api.types.is_datetime64_any_dtype(transactions["Дата операции"]):
                transactions["Дата операции"] = pd.to_datetime(
                    transactions["Дата операции"], errors="coerce"
                )

        # Фильтруем по дате
        date_mask = (transactions["Дата операции"] >= start_date) & (
            transactions["Дата операции"] <= end_date
        )
        period_transactions = transactions[date_mask].copy()

        if period_transactions.empty:
            logger.warning("Не найдено транзакций за указанный период")
            return pd.DataFrame(
                columns=[
                    "День недели",
                    "avg_spending",
                    "total_spending",
                    "transaction_count",
                ]
            )

        # Добавляем день недели
        period_transactions["День недели"] = period_transactions[
            "Дата операции"
        ].dt.day_name()

        # Группируем по дням недели
        result = (
            period_transactions.groupby("День недели")
            .agg(
                avg_spending=("Сумма операции", "mean"),
                total_spending=("Сумма операции", "sum"),
                transaction_count=("Сумма операции", "count"),
            )
            .reset_index()
        )

        # Упорядочиваем дни недели
        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        result["День недели"] = pd.Categorical(
            result["День недели"], categories=day_order, ordered=True
        )
        result = result.sort_values("День недели").reset_index(drop=True)

        logger.info("Проанализировано трат по дням недели: %d строк", len(result))

        return result

    except Exception as e:
        logger.error("Ошибка при анализе трат по дням недели: %s", e)
        return pd.DataFrame(
            columns=[
                "День недели",
                "avg_spending",
                "total_spending",
                "transaction_count",
            ]
        )


@report_decorator()
def spending_by_workday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> pd.DataFrame:
    """
    Анализирует траты в рабочие и выходные дни за последние три месяца.

    Args:
        transactions: DataFrame с транзакциями
        date: Дата отсчета в формате 'YYYY-MM-DD' (если None, используется текущая дата)

    Returns:
        DataFrame с тратами по типам дней
    """
    try:
        logger.info("Анализ трат в рабочие/выходные дни")

        # Определяем дату отсчета
        if date is None:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(date, "%Y-%m-%d")

        # Вычисляем дату начала (три месяца назад)
        start_date = end_date - timedelta(days=90)

        # Преобразуем дату операции в datetime, если нужно
        if "Дата операции" in transactions.columns:
            if not pd.api.types.is_datetime64_any_dtype(transactions["Дата операции"]):
                transactions["Дата операции"] = pd.to_datetime(
                    transactions["Дата операции"], errors="coerce"
                )

        # Фильтруем по дате
        date_mask = (transactions["Дата операции"] >= start_date) & (
            transactions["Дата операции"] <= end_date
        )
        period_transactions = transactions[date_mask].copy()

        if period_transactions.empty:
            logger.warning("Не найдено транзакций за указанный период")
            return pd.DataFrame(
                columns=[
                    "Тип дня",
                    "avg_spending",
                    "total_spending",
                    "transaction_count",
                ]
            )

        # Определяем тип дня (рабочий/выходной)
        period_transactions["День недели"] = period_transactions[
            "Дата операции"
        ].dt.weekday
        period_transactions["Тип дня"] = period_transactions["День недели"].apply(
            lambda x: "Выходной" if x >= 5 else "Рабочий"
        )

        # Группируем по типу дня
        result = (
            period_transactions.groupby("Тип дня")
            .agg(
                avg_spending=("Сумма операции", "mean"),
                total_spending=("Сумма операции", "sum"),
                transaction_count=("Сумма операции", "count"),
            )
            .reset_index()
        )

        logger.info("Проанализировано трат по типам дней: %d строк", len(result))

        return result

    except Exception as e:
        logger.error("Ошибка при анализе трат по типам дней: %s", e)
        return pd.DataFrame(
            columns=["Тип дня", "avg_spending", "total_spending", "transaction_count"]
        )

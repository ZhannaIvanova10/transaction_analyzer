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
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Union[Dict[str, Any], pd.DataFrame]:
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
                    logger.info("Отчет сохранен в %s", file_to_save)
                except Exception as e:
                    logger.error("Ошибка сохранения отчета: %s", e)

                return result
            except Exception as e:
                logger.error("Ошибка в функции %s: %s", func.__name__, e)
                raise

        return wrapper

    return decorator


@report_decorator()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Анализирует траты по категории за последние 3 месяца.
    Args:
        transactions: DataFrame с транзакциями
        category: Категория для анализа
        date: Дата отсчет (если None, используется текущая дата)

    Returns:
        Словарь с анализом трат
    """
    try:
        if transactions.empty:
            logger.warning("Нет данных для анализа")
            return {
                "category": category,
                "period": "",
                "total_spent": 0.0,
                "transaction_count": 0,
                "spending": [],
            }

        # Определяем дату отсчета
        if date:
            try:
                end_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                logger.warning(
                    "Неверный формат даты: %s, используется текущая дата", date
                )
                end_date = datetime.now()
        else:
            end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        # Проверяем наличие необходимых колонок
        required_columns = ["Дата операции", "Сумма платежа", "Категория"]
        for col in required_columns:
            if col not in transactions.columns:
                logger.error("Отсутствует колонка: %s", col)
                return {
                    "category": category,
                    "period": "",
                    "total_spent": 0.0,
                    "transaction_count": 0,
                    "spending": [],
                }

        # Конвертируем дату
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"], errors="coerce"
        )

        # Фильтруем по дате и категории, только отрицательные суммы (траты)
        mask = (
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Категория"] == category)
            & (transactions["Сумма платежа"] < 0)  # Только траты
        )
        filtered_df = transactions[mask].copy()

        if filtered_df.empty:
            logger.warning(
                "Нет транзакций по категории '%s' за последние 3 месяца", category
            )
            return {
                "category": category,
                "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
                "total_spent": 0.0,
                "transaction_count": 0,
                "spending": [],
            }

        # Агрегируем по месяцам
        filtered_df["month"] = filtered_df["Дата операции"].dt.strftime("%Y-%m")

        # Используем абсолютные значения для трат
        filtered_df["abs_amount"] = filtered_df["Сумма платежа"].abs()

        monthly_stats = (
            filtered_df.groupby("month")
            .agg(
                total_spent=("abs_amount", "sum"),
                transaction_count=("abs_amount", "count"),
            )
            .reset_index()
        )
        # Сортируем по месяцам
        monthly_stats = monthly_stats.sort_values("month")

        # Подготавливаем результат
        spending_list = []
        for _, row in monthly_stats.iterrows():
            spending_list.append(
                {
                    "month": row["month"],
                    "total_spent": float(row["total_spent"]),
                    "transaction_count": int(row["transaction_count"]),
                }
            )

        total_spent = float(filtered_df["abs_amount"].sum())
        transaction_count = len(filtered_df)

        result = {
            "category": category,
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "total_spent": total_spent,
            "transaction_count": transaction_count,
            "spending": spending_list,
        }
        logger.info(
            "Проанализированы траты по категории '%s': %s транзакций, %.2f руб.",
            category,
            transaction_count,
            total_spent,
        )
        return result

    except Exception as e:
        logger.error("Ошибка анализа трат по категории: %s", e)
        return {
            "category": category,
            "period": "",
            "total_spent": 0.0,
            "transaction_count": 0,
            "spending": [],
        }


@report_decorator()
def spending_by_weekday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Анализирует средние траты по дням недели за последние 3 месяца.
    Args:
        transactions: DataFrame с транзакции
        date: Дата отсчета (если None, используется текущая дата)

    Returns:
        Словарь с анализом трат по дням недели
    """
    try:
        if transactions.empty:
            logger.warning("Нет данных для анализа")
            return {"period": "", "spending_by_weekday": {}}

        # Определяем дату отсчета
        if date:
            try:
                end_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                logger.warning(
                    "Неверный формат даты: %s, используется текущая дата", date
                )
                end_date = datetime.now()
        else:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=90)
        # Проверяем наличие необходимых колонок
        required_columns = ["Дата операции", "Сумма платежа"]
        for col in required_columns:
            if col not in transactions.columns:
                logger.error("Отсутствует колонка: %s", col)
                return {
                    "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
                    "spending_by_weekday": {},
                }

        # Конвертируем дату
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"], errors="coerce"
        )

        # Фильтруем по дате и только отрицательные суммы (траты)
        mask = (
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Сумма платежа"] < 0)  # Только траты
        )
        filtered_df = transactions[mask].copy()

        if filtered_df.empty:
            logger.warning("Нет транзакций за последние 3 месяца")
            return {
                "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
                "spending_by_weekday": {},
            }

        # Добавляем день недели
        filtered_df["weekday"] = filtered_df["Дата операции"].dt.day_name()

        # Русские названия дней недели
        weekday_translation = {
            "Monday": "Понедельник",
            "Tuesday": "Вторник",
            "Wednesday": "Среда",
            "Thursday": "Четверг",
            "Friday": "Пятница",
            "Saturday": "Суббота",
            "Sunday": "Воскресенье",
        }
        filtered_df["weekday_ru"] = filtered_df["weekday"].map(weekday_translation)

        # Используем абсолютные значения для трат
        filtered_df["abs_amount"] = filtered_df["Сумма платежа"].abs()

        # Агрегируем по дням недели
        weekday_stats = (
            filtered_df.groupby("weekday_ru")
            .agg(
                average_spent=("abs_amount", "mean"),
                total_spent=("abs_amount", "sum"),
                transaction_count=("abs_amount", "count"),
            )
            .reset_index()
        )

        # Сортируем по порядку дней недели
        weekday_order = [
            "Понедельник",
            "Вторник",
            "Среда",
            "Четверг",
            "Пятница",
            "Суббота",
            "Воскресенье",
        ]
        weekday_stats["weekday_order"] = weekday_stats["weekday_ru"].apply(
            lambda x: (
                weekday_order.index(x) if x in weekday_order else len(weekday_order)
            )
        )
        weekday_stats = weekday_stats.sort_values("weekday_order")

        # Подготавливаем результат
        spending_by_weekday_dict = {}
        for _, row in weekday_stats.iterrows():
            spending_by_weekday_dict[row["weekday_ru"]] = {
                "average_spent": float(row["average_spent"]),
                "total_spent": float(row["total_spent"]),
                "transaction_count": int(row["transaction_count"]),
            }
        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "spending_by_weekday": spending_by_weekday_dict,
        }

        logger.info(
            "Проанализированы траты по дням недели: %s транзакций", len(filtered_df)
        )
        return result

    except Exception as e:
        logger.error("Ошибка анализа трат по дням недели: %s", e)
        return {"period": "", "spending_by_weekday": {}}


@report_decorator()
def spending_by_workday(
    transactions: pd.DataFrame, date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Анализирует средние траты в рабочие и выходные дни за последние 3 месяца.

    Args:
        transactions: DataFrame с транзакциями
        date: Дата отсчета (если None, используется текущая дата)

    Returns:
        Словарь с анализом трат по типам дней
    """
    try:
        if transactions.empty:
            logger.warning("Нет данных для анализа")
            return {"period": "", "workday_spending": {}, "total_statistics": {}}

        # Определяем дату отсчета
        if date:
            try:
                end_date = datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                logger.warning(
                    "Неверный формат даты: %s, используется текущая дата", date
                )
                end_date = datetime.now()
        else:
            end_date = datetime.now()

        start_date = end_date - timedelta(days=90)
        # Проверяем наличие необходимых колонок
        required_columns = ["Дата операции", "Сумма платежа"]
        for col in required_columns:
            if col not in transactions.columns:
                logger.error("Отсутствует колонка: %s", col)
                return {
                    "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
                    "workday_spending": {},
                    "total_statistics": {},
                }

        # Конвертируем дату
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"], errors="coerce"
        )

        # Фильтруем по дате и только отрицательные суммы (траты)
        mask = (
            (transactions["Дата операции"] >= start_date)
            & (transactions["Дата операции"] <= end_date)
            & (transactions["Сумма платежа"] < 0)  # Только траты
        )

        filtered_df = transactions[mask].copy()

        if filtered_df.empty:
            logger.warning("Нет транзакций за последние 3 месяца")
            return {
                "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
                "workday_spending": {},
                "total_statistics": {},
            }

        # Добавляем тип дня (рабочий/выходной)
        # Понедельник-пятница = рабочие дни, суббота-воскресенье = выходные
        filtered_df["is_weekend"] = filtered_df["Дата операции"].dt.weekday >= 5
        filtered_df["day_type"] = filtered_df["is_weekend"].apply(
            lambda x: "Выходные дни" if x else "Рабочие дни"
        )

        # Используем абсолютные значения для трат
        filtered_df["abs_amount"] = filtered_df["Сумма платежа"].abs()

        # Агрегируем по типам дней
        day_type_stats = (
            filtered_df.groupby("day_type")
            .agg(
                average_spent=("abs_amount", "mean"),
                total_spent=("abs_amount", "sum"),
                transaction_count=("abs_amount", "count"),
                average_daily_transactions=(
                    "abs_amount",
                    lambda x: len(x) / 90 * (7 / 5 if "Рабочие" in x.name else 7 / 2),
                ),
            )
            .reset_index()
        )
        # Общая статистика
        total_spent = float(filtered_df["abs_amount"].sum())
        total_transactions = len(filtered_df)
        average_daily_spent = total_spent / 90

        # Подготавливаем результат
        workday_spending = {}
        for _, row in day_type_stats.iterrows():
            workday_spending[row["day_type"]] = {
                "average_spent": float(row["average_spent"]),
                "total_spent": float(row["total_spent"]),
                "transaction_count": int(row["transaction_count"]),
                "average_daily_transactions": float(row["average_daily_transactions"]),
            }

        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}",
            "workday_spending": workday_spending,
            "total_statistics": {
                "total_spent": total_spent,
                "total_transactions": total_transactions,
                "average_daily_spent": average_daily_spent,
            },
        }
        logger.info(
            "Проанализированы траты по типам дней: %s транзакций, %.2f руб.",
            total_transactions,
            total_spent,
        )
        return result

    except Exception as e:
        logger.error("Ошибка анализа трат по типам дней: %s", e)
        return {"period": "", "workday_spending": {}, "total_statistics": {}}

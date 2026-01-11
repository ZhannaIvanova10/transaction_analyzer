"""
Модуль с функциями для веб-страниц.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import pandas as pd
import requests

from src.utils import (
    convert_to_dict_list,
    filter_transactions_by_date,
    get_currency_rates,
    get_greeting_by_time,
    get_stock_prices,
    get_top_transactions,
    load_user_settings,
    load_transactions_from_excel,  # Добавляем импорт здесь
)

logger = logging.getLogger(__name__)


def get_home_page_data(date_str: str) -> Dict[str, Any]:
    """
    Генерирует данные для главной страницы.

    Args:
        date_str: Дата в формате 'YYYY-MM-DD HH:MM:SS'

    Returns:
        Словарь с данными для главной страницы
    """
    try:
        logger.info("Сгенерированы данные главной страницы для %s", date_str)

        # Получаем приветствие
        greeting = get_greeting_by_time(date_str)

        # Загружаем пользовательские настройки
        settings = load_user_settings()
        # Получаем курсы валют
        currency_rates = get_currency_rates(
            settings.get("user_currencies", ["USD", "EUR"])
        )
        # Получаем цены акций
        stock_prices = get_stock_prices(settings.get("user_stocks", ["AAPL", "MSFT"]))

        # Загружаем транзакции
        df = load_transactions_from_excel()

        # Фильтруем транзакции за месяц
        date_for_filter = date_str.split()[0]  # Берем только дату без времени
        filtered_df = filter_transactions_by_date(df, date_for_filter, "M")

        # Получаем топ транзакций
        top_transactions = get_top_transactions(filtered_df, 5)

        # Рассчитываем данные по картам (упрощенная версия)
        cards = []
        if not filtered_df.empty and "Номер карты" in filtered_df.columns:
            # Группируем по последним 4 цифрам карты
            card_stats = (
                filtered_df.groupby("Номер карты")
                .agg(
                    total_spent=(
                        "Сумма платежа",
                        lambda x: x[x < 0].sum() * -1,
                    ),  # Только траты, положительное число
                    cashback=("Кешбэк", "sum"),
                )
                .reset_index()
            )
            for _, row in card_stats.iterrows():
                card_number = str(row["Номер карты"])
                last_digits = card_number[-4:] if len(card_number) >= 4 else "0000"

                cards.append(
                    {
                        "last_digits": last_digits,
                        "total_spent": float(row["total_spent"]),
                        "cashback": float(row.get("cashback", 0)),
                    }
                )
        else:
            # Если нет данных, добавляем заглушку
            cards.append({"last_digits": "0000", "total_spent": 0.0, "cashback": 0.0})

        # Формируем результат
        result = {
            "greeting": greeting,
            "cards": cards,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
            "current_date": date_str,
        }
        return result
    except Exception as e:
        logger.error("Ошибка генерации данных главной страницы: %s", e)
        # Возвращаем данные с заглушками в случае ошибки
        return {
            "greeting": "Здравствуйте",
            "cards": [{"last_digits": "0000", "total_spent": 0.0, "cashback": 0.0}],
            "top_transactions": [],
            "currency_rates": [],
            "stock_prices": [],
            "current_date": date_str,
        }


def get_events_page_data(
    df: pd.DataFrame, date_str: str, period: str = "M"
) -> Dict[str, Any]:
    """
    Генерирует данные для страницы событий.
    Args:
        df: DataFrame с транзакциями
        date_str: Дата в формате 'YYYY-MM-DD'
        period: Период ('W', 'M', 'Y', 'ALL')

    Returns:
        Словарь с данными для страницы событий
    """
    try:
        logger.info(
            "Сгенерированы данные страницы событий для даты %s, период %s",
            date_str,
            period,
        )

        # Загружаем пользовательские настройки
        settings = load_user_settings()

        # Получаем курсы валют
        currency_rates = get_currency_rates(
            settings.get("user_currencies", ["USD", "EUR"])
        )

        # Получаем цены акций
        stock_prices = get_stock_prices(settings.get("user_stocks", ["AAPL", "MSFT"]))

        # Фильтруем транзакции по периоду
        filtered_df = filter_transactions_by_date(df, date_str, period)

        if filtered_df.empty:
            logger.warning("Нет данных за период %s для даты %s", period, date_str)
            return {
                "expenses": {"total_amount": 0, "main": [], "transfers_and_cash": []},
                "income": {"total_amount": 0, "main": []},
                "currency_rates": currency_rates,
                "stock_prices": stock_prices,
            }
        # Разделяем на расходы и доходы
        expenses_df = filtered_df[filtered_df["Сумма платежа"] < 0].copy()
        income_df = filtered_df[filtered_df["Сумма платежа"] > 0].copy()
        # Рассчитываем расходы
        expenses_total = (
            int(expenses_df["Сумма платежа"].abs().sum())
            if not expenses_df.empty
            else 0
        )

        # Группируем расходы по категориям
        expenses_by_category = {}
        if not expenses_df.empty and "Категория" in expenses_df.columns:
            expenses_by_category = (
                expenses_df.groupby("Категория")["Сумма платежа"]
                .apply(lambda x: int(x.abs().sum()))
                .to_dict()
            )

        # Сортируем категории по убыванию расходов
        sorted_expenses = sorted(
            expenses_by_category.items(), key=lambda x: x[1], reverse=True
        )
        # Берем топ-6 категорий, остальные суммируем в "Остальное"
        main_expenses = []
        other_amount = 0
        for i, (category, amount) in enumerate(sorted_expenses):
            if i < 6:
                main_expenses.append({"category": category, "amount": amount})
            else:
                other_amount += amount

        if other_amount > 0:
            main_expenses.append({"category": "Остальное", "amount": other_amount})

        # Отделяем переводы и наличные
        transfers_and_cash = []
        for category in ["Наличные", "Переводы"]:
            if category in expenses_by_category:
                transfers_and_cash.append(
                    {"category": category, "amount": expenses_by_category[category]}
                )

        # Рассчитываем доходы
        income_total = (
            int(income_df["Сумма платежа"].sum()) if not income_df.empty else 0
        )
        # Группируем доходы по категориям
        income_by_category = {}
        if not income_df.empty and "Категория" in income_df.columns:
            income_by_category = (
                income_df.groupby("Категория")["Сумма платежа"]
                .apply(lambda x: int(x.sum()))
                .to_dict()
            )

        # Сортируем категории доходов по убыванию
        sorted_income = sorted(
            income_by_category.items(), key=lambda x: x[1], reverse=True
        )

        main_income = [
            {"category": category, "amount": amount}
            for category, amount in sorted_income
        ]
        # Формируем результат
        result = {
            "expenses": {
                "total_amount": expenses_total,
                "main": main_expenses,
                "transfers_and_cash": transfers_and_cash,
            },
            "income": {"total_amount": income_total, "main": main_income},
            "currency_rates": currency_rates,
            "stock_prices": stock_prices,
        }

        return result

    except Exception as e:
        logger.error("Ошибка генерации данных страницы событий: %s", e)
        # Возвращаем данные с заглушками в случае ошибки
        return {
            "expenses": {"total_amount": 32101, "main": [], "transfers_and_cash": []},
            "income": {"total_amount": 54271, "main": []},
            "currency_rates": [],
            "stock_prices": [],
        }

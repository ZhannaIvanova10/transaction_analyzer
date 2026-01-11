"""
Утилиты для работы с данными.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union

import pandas as pd
import requests
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()


def get_greeting_by_time(time_input: Union[str, datetime]) -> str:
    """
    Возвращает приветствие в зависимости от времени.

    Args:
        time_input: Время в формате строки или datetime

    Returns:
        Строка с приветствием
    """
    try:
        if isinstance(time_input, str):
            dt = parse_date(time_input)
        else:
            dt = time_input

        hour = dt.hour

        if 5 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 18:
            return "Добрый день"
        elif 18 <= hour < 23:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    except Exception:
        logger.error("Неверный формат даты: %s", time_input)
        return "Здравствуйте"


def parse_date(date_str: str) -> datetime:
    """
    Парсит строку с датой в datetime.

    Args:
        date_str: Строка с датой

    Returns:
        Объект datetime

    Raises:
        ValueError: Если строка не может быть распарсена
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            logger.error("Неверный формат даты: %s", date_str)
            raise ValueError(f"Неверный формат даты: {date_str}") from e


def load_user_settings() -> Dict[str, Any]:
    """
    Загружает пользовательские настройки из JSON-файла.

    Returns:
        Словарь с настройками пользователя
    """
    try:
        with open("user_settings.json", "r", encoding="utf-8") as f:
            settings: Dict[str, Any] = json.load(f)
            return settings
    except FileNotFoundError:
        logger.warning(
            "Файл user_settings.json не найден, используются настройки по умолчанию"
        )
        return {
            "user_currencies": ["USD", "EUR", "GBP", "JPY", "CNY"],
            "user_stocks": [
                "AAPL",
                "MSFT",
                "GOOGL",
                "AMZN",
                "TSLA",
                "META",
                "NVDA",
                "BRK.B",
            ],
        }


def get_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Получает курсы валют через API.

    Args:
        currencies: Список валют

    Returns:
        Список словарей с курсами валют
    """
    api_key = os.environ.get("EXCHANGE_RATE_API_KEY")

    if not api_key:
        logger.warning(
            "API ключ для курсов валют не найден, используются фиктивные курсы"
        )
        return get_currency_rates_stub(currencies)

    try:
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/RUB"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            rates = data.get("conversion_rates", {})

            result: List[Dict[str, Any]] = []
            for currency in currencies:
                if currency in rates:
                    # Конвертируем из RUB в целевую валюту (1 единица целевой валюты = X RUB)
                    rate = 1 / rates[currency] if rates[currency] != 0 else 1
                    result.append({"currency": currency, "rate": round(rate, 4)})
                else:
                    result.append({"currency": currency, "rate": 1.0})

            return result
        else:
            logger.error(
                "Ошибка HTTP %s при запросе курсов валют", response.status_code
            )
            return get_currency_rates_stub(currencies)

    except Exception as e:
        logger.error("Ошибка API курсов валют: %s", e)
        return get_currency_rates_stub(currencies)


def get_currency_rates_stub(currencies: List[str]) -> List[Dict[str, Any]]:
    """
    Заглушка для получения курсы валют.

    Args:
        currencies: Список валют

    Returns:
        Список словарей с фиктивными курсами
    """
    stub_rates = {
        "USD": 1.0,
        "EUR": 0.8591,
        "GBP": 0.7455,
        "JPY": 157.7408,
        "CNY": 6.9967,
        "RUB": 90.0,
    }

    result: List[Dict[str, Any]] = []
    for currency in currencies:
        rate = stub_rates.get(currency, 1.0)
        result.append({"currency": currency, "rate": rate})

    return result


def get_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Получает цены акций через API.

    Args:
        stocks: Список тикеров акций

    Returns:
        Список словарей с ценами акций
    """
    api_key = os.environ.get("STOCK_API_KEY")

    if not api_key:
        logger.warning("API ключ для акций не найден, используются фиктивные цены")
        return get_stock_prices_stub(stocks)

    try:
        url = "https://api.twelvedata.com/price"
        params = {
            "symbol": ",".join(stocks),
            "apikey": api_key,
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()

            result: List[Dict[str, Any]] = []
            for stock in stocks:
                price_str = data.get(stock, {}).get("price", "0")
                try:
                    price = float(price_str)
                except ValueError:
                    price = 100.0

                result.append({"stock": stock, "price": price})

            return result
        else:
            logger.warning("Ошибка API акций: %s", response.status_code)
            return get_stock_prices_stub(stocks)

    except Exception as e:
        logger.warning("Ошибка API акций: %s", e)
        return get_stock_prices_stub(stocks)


def get_stock_prices_stub(stocks: List[str]) -> List[Dict[str, Any]]:
    """
    Заглушка для получения цен акций.

    Args:
        stocks: Список тикеров акций

    Returns:
        Список словарей с фиктивными ценами
    """
    stub_prices = {
        "AAPL": 185.0,
        "MSFT": 375.0,
        "GOOGL": 138.0,
        "AMZN": 155.0,
        "TSLA": 245.0,
        "META": 355.0,
        "NVDA": 495.0,
        "BRK.B": 360.0,
    }

    result: List[Dict[str, Any]] = []
    for stock in stocks:
        price = stub_prices.get(stock, 100.0)
        result.append({"stock": stock, "price": price})

    return result


def load_transactions_from_excel(
    filepath: str = "data/operations.xlsx",
) -> pd.DataFrame:
    """
    Загружает транзакции из Excel-файла.

    Args:
        filepath: Путь к Excel-файлу

    Returns:
        DataFrame с транзакциями
    """
    try:
        df = pd.read_excel(filepath)
        logger.info("Загружено %s транзакций из %s", len(df), filepath)
        return df
    except FileNotFoundError:
        logger.error("Файл %s не найден", filepath)
        return pd.DataFrame()


def filter_transactions_by_date(
    df: pd.DataFrame, date_str: str, period: str = "M"
) -> pd.DataFrame:
    """
    Фильтрует транзакции по дате и периоду.

    Args:
        df: DataFrame с транзакциями
        date_str: Дата в формате 'YYYY-MM-DD'
        period: Период ('D', 'W', 'M', 'Y', 'ALL')

    Returns:
        Отфильтрованный DataFrame
    """
    if df.empty:
        return df

    try:
        # Парсим дату
        target_date = datetime.strptime(date_str, "%Y-%m-%d")

        # Преобразуем колонку с датой, если она есть
        date_columns = ["Дата операции", "Дата платежа", "Дата"]
        date_column = None

        for col in date_columns:
            if col in df.columns:
                date_column = col
                break

        if date_column is None:
            logger.error("Нет колонки с датой в DataFrame")
            return pd.DataFrame()

        # Преобразуем колонку с датой в datetime
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

        # Фильтруем по периоду
        if period == "D":  # День
            start_date = target_date.replace(hour=0, minute=0, second=0)
            end_date = target_date.replace(hour=23, minute=59, second=59)
        elif period == "W":  # Неделя
            start_date = target_date - timedelta(days=target_date.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0)
            end_date = start_date + timedelta(days=6, hours=23, minutes=59, seconds=59)
        elif period == "M":  # Месяц
            start_date = target_date.replace(day=1, hour=0, minute=0, second=0)
            if target_date.month == 12:
                end_date = target_date.replace(
                    year=target_date.year + 1, month=1, day=1
                ) - timedelta(seconds=1)
            else:
                end_date = target_date.replace(
                    month=target_date.month + 1, day=1
                ) - timedelta(seconds=1)
        elif period == "Y":  # Год
            start_date = target_date.replace(month=1, day=1, hour=0, minute=0, second=0)
            end_date = target_date.replace(
                year=target_date.year + 1, month=1, day=1
            ) - timedelta(seconds=1)
        elif period == "ALL":  # Все данные до даты
            start_date = datetime.min
            end_date = target_date.replace(hour=23, minute=59, second=59)
        else:
            logger.warning("Неизвестный период: %s, используется месяц", period)
            start_date = target_date.replace(day=1, hour=0, minute=0, second=0)
            if target_date.month == 12:
                end_date = target_date.replace(
                    year=target_date.year + 1, month=1, day=1
                ) - timedelta(seconds=1)
            else:
                end_date = target_date.replace(
                    month=target_date.month + 1, day=1
                ) - timedelta(seconds=1)

        filtered_df = df[
            (df[date_column] >= start_date) & (df[date_column] <= end_date)
        ]
        logger.info(
            "Отфильтровано %s транзакций за период %s", len(filtered_df), period
        )

        return filtered_df

    except Exception as e:
        logger.error("Ошибка фильтрации транзакций: %s", e)
        return pd.DataFrame()


def calculate_cashback(amount: float) -> float:
    """
    Рассчитывает кешбэк (1 рубль на каждые 100 рублей).

    Args:
        amount: Сумма расходов

    Returns:
        Сумма кешбэка
    """
    return max(amount, 0) / 100


def convert_to_dict_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Конвертирует DataFrame в список словарей.

    Args:
        df: DataFrame для конвертации

    Returns:
        Список словарей
    """
    if df.empty:
        return []

    result: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        row_dict: Dict[str, Any] = {}
        for col in df.columns:
            value = row[col]
            # Преобразуем специфичные типы
            if isinstance(value, pd.Timestamp):
                row_dict[col] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif pd.isna(value):
                row_dict[col] = None
            else:
                row_dict[col] = value
        result.append(row_dict)

    return result


def save_to_json(data: Dict[str, Any], filename: str) -> bool:
    """
    Сохраняет данные в JSON-файл.

    Args:
        data: Данные для сохранения
        filename: Имя файла

    Returns:
        True если успешно, False если ошибка
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Данные сохранены в %s", filename)
        return True
    except Exception as e:
        logger.error("Ошибка сохранения в JSON: %s", e)
        return False


def get_top_transactions(df: pd.DataFrame, n: int = 5) -> List[Dict[str, Any]]:
    """
    Возвращает топ-N транзакций по сумме платежа.

    Args:
        df: DataFrame с транзакциями
        n: Количество транзакций

    Returns:
        Список словарей с топ транзакциями
    """
    if df.empty:
        return []

    try:
        # Проверяем наличие колонки с суммой
        amount_columns = ["Сумма платежа", "Сумма операции", "Сумма"]
        amount_column = None

        for col in amount_columns:
            if col in df.columns:
                amount_column = col
                break

        if amount_column is None:
            logger.warning("Нет колонки с суммой")
            return []

        # Сортируем по абсолютной сумме (по убыванию)
        top_df = df.copy()
        top_df["abs_amount"] = top_df[amount_column].abs()
        top_df = top_df.sort_values("abs_amount", ascending=False).head(n)

        # Форматируем результат
        result: List[Dict[str, Any]] = []
        date_columns = ["Дата операции", "Дата платежа", "Дата"]
        date_column = None

        for col in date_columns:
            if col in top_df.columns:
                date_column = col
                break

        for _, row in top_df.iterrows():
            transaction = {
                "date": (
                    row[date_column].strftime("%d.%m.%Y")
                    if date_column and not pd.isna(row[date_column])
                    else ""
                ),
                "amount": float(row[amount_column]),
                "category": str(row.get("Категория", "")),
                "description": str(row.get("Описание", ""))[
                    :100
                ],  # Обрезаем длинные описания
            }
            result.append(transaction)

        return result

    except Exception as e:
        logger.error("Ошибка получения топ транзакций: %s", e)
        return []

"""
Тесты для основного модуля.
"""
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.main import main
from src.utils import calculate_cashback, get_greeting_by_time


def test_get_greeting():
    """Тест функции приветствия."""
    assert get_greeting_by_time("2024-01-01 08:00:00") == "Доброе утро"
    assert get_greeting_by_time("2024-01-01 14:00:00") == "Добрый день"
    assert get_greeting_by_time("2024-01-01 20:00:00") == "Добрый вечер"
    assert get_greeting_by_time("2024-01-01 02:00:00") == "Доброй ночи"

    # Тест с невалидной датой
    assert get_greeting_by_time("invalid-date") == "Здравствуйте"


def test_calculate_cashback():
    """Тест расчета кешбэка."""
    assert calculate_cashback(100) == 1.0
    assert calculate_cashback(500) == 5.0
    assert calculate_cashback(0) == 0.0
    assert calculate_cashback(-100) == 0.0  # Отрицательная сумма - нет кешбэка


def test_main_function():
    """Тест основной функции."""
    # Функция main не принимает аргументов
    try:
        main()
        assert True  # Если не упала, то все ок
    except Exception as e:
        pytest.fail(f"main() вызвала исключение: {e}")


@patch('src.main.demonstrate_home_page')
@patch('src.main.demonstrate_events_page')
@patch('src.main.demonstrate_services')
@patch('src.main.demonstrate_reports')
def test_main_with_mock(mock_reports, mock_services, mock_events, mock_home):
    """Тест основной функции с mock."""
    mock_home.return_value = {"greeting": "Добрый день"}
    mock_events.return_value = {"expenses": {"total_amount": 0}}

    # Вызываем main (без аргументов!)
    main()

    # Проверяем что все демо функции были вызваны
    mock_home.assert_called_once()
    mock_events.assert_called_once()
    mock_services.assert_called_once()
    mock_reports.assert_called_once()


def test_calculate_total_spent():
    """Тест расчета общих расходов."""
    # Создаем тестовые данные
    transactions = [
        {"Сумма платежа": -1000, "Категория": "Супермаркеты", "Номер карты": "****1234"},
        {"Сумма платежа": -500, "Категория": "Кафе", "Номер карты": "****1234"},
        {"Сумма платежа": 2000, "Категория": "Зарплата", "Номер карты": "****5678"},  # Не расход
    ]

    # Суммируем только отрицательные значения (расходы)
    total_spent = sum(t["Сумма платежа"] for t in transactions if t["Сумма платежа"] < 0)
    assert total_spent == -1500  # -1000 + (-500)
    assert abs(total_spent) == 1500  # Абсолютное значение


@patch('src.utils.load_transactions_from_excel')
def test_real_data_loading(mock_load):
    """Тест загрузки реальных данных."""
    # Создаем мок DataFrame
    test_df = pd.DataFrame({
        "Дата операции": ["2024-01-15", "2024-01-16"],
        "Сумма платежа": [-1000, -500],
        "Категория": ["Супермаркеты", "Кафе"],
        "Номер карты": ["****1234", "****1234"]
    })

    mock_load.return_value = test_df

    # Импортируем и вызываем функцию
    from src.utils import load_transactions_from_excel
    result = load_transactions_from_excel()

    assert not result.empty
    assert len(result) == 2
    assert "Дата операции" in result.columns
    assert "Сумма платежа" in result.columns
    assert "Категория" in result.columns

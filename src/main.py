"""
Основной модуль приложения.
"""

import json
import logging
from typing import Any, Dict

from src.reports import (spending_by_category, spending_by_weekday,
                         spending_by_workday)
from src.services import (investment_bank, profitable_cashback_categories,
                          search_by_person_transfers, search_by_phone_numbers,
                          simple_search)
from src.utils import convert_to_dict_list, load_transactions_from_excel
from src.views import get_events_page_data, get_home_page_data

logger = logging.getLogger(__name__)


def demonstrate_home_page() -> Dict[str, Any]:
    """
    Демонстрация работы страницы 'Главная'.
    """
    date_str = "2024-01-15 14:30:00"
    logger.info("Демонстрация главной страницы для даты: %s", date_str)
    result = get_home_page_data(date_str)
    print("\n=== Демонстрация главной страницы ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


def demonstrate_services() -> None:
    """
    Демонстрация работы сервисов.
    """
    logger.info("Демонстрация сервисов")

    # Загружаем данные
    df = load_transactions_from_excel()
    transactions = convert_to_dict_list(df)

    print("\n=== Демонстрация сервисов ===")

    # 1. Выгодные категории кешбэка
    cashback_categories = profitable_cashback_categories(transactions, 2024, 1)
    print("\n1. Выгодные категории кешбэка (январь 2024):")
    for category, cashback in list(cashback_categories.items())[:5]:
        print(f"   {category}: {cashback:.2f} руб.")

    # 2. Инвесткопилка
    investment = investment_bank("2024-01", transactions, 10)
    print(f"\n2. Инвесткопилка за январь 2024: {investment:.2f} руб.")

    # 3. Простой поиск
    search_results = simple_search("кафе", transactions)
    print(f"\n3. Простой поиск 'кафе': найдено {len(search_results)} транзакций")

    # 4. Поиск по телефонным номерам
    phone_transactions = search_by_phone_numbers(transactions)
    print(f"\n4. Транзакции с телефонными номерами: {len(phone_transactions)}")

    # 5. Поиск переводов физлицам
    person_transfers = search_by_person_transfers(transactions)
    print(f"\n5. Переводы физическим лицам: {len(person_transfers)}")


def demonstrate_reports() -> None:
    """
    Демонстрация работы отчетов.
    """
    logger.info("Демонстрация отчетов")

    # Загружаем данные
    df = load_transactions_from_excel()

    print("\n=== Демонстрация отчетов ===")

    # 1. Траты по категории
    category_report = spending_by_category(df, "Супермаркеты")
    print("\n1. Траты по категории 'Супермаркеты':")
    print(f"   Период: {category_report.get('period', 'N/A')}")
    print(f"   Всего потрачено: {category_report.get('total_spent', 0):.2f} руб.")
    print(f"   Количество транзакций: {category_report.get('transaction_count', 0)}")

    # 2. Траты по дням недели
    weekday_report = spending_by_weekday(df)
    print("\n2. Траты по дням недели:")
    print(f"   Период: {weekday_report.get('period', 'N/A')}")
    weekday_stats = weekday_report.get("spending_by_weekday", {})
    for day, stats in weekday_stats.items():
        print(f"   {day}: в среднем {stats.get('average_spent', 0):.2f} руб.")

    # 3. Траты в рабочие/выходные дни
    workday_report = spending_by_workday(df)
    print("\n3. Траты в рабочие/выходные дни:")
    print(f"   Период: {workday_report.get('period', 'N/A')}")
    workday_stats = workday_report.get("workday_spending", {})
    for day_type, stats in workday_stats.items():
        print(f"   {day_type}: в среднем {stats.get('average_spent', 0):.2f} руб.")


def demonstrate_events_page() -> Dict[str, Any]:
    """
    Демонстрация работы страницы 'События'.
    """
    date_str = "2024-01-15"
    logger.info("Демонстрация страницы событий для даты: %s", date_str)

    # Загружаем и фильтруем данные
    df = load_transactions_from_excel()
    result = get_events_page_data(df, date_str)

    print("\n=== Демонстрация страницы 'События' ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    return result


def main() -> None:
    """
    Основная функция приложения.
    """
    logger.info("Запуск приложения для анализа транзакций")

    print("=" * 60)
    print("ПРИЛОЖЕНИЕ ДЛЯ АНАЛИЗА ТРАНЗАКЦИЙ")
    print("=" * 60)

    # Демонстрация всех функциональностей
    demonstrate_home_page()
    demonstrate_events_page()
    demonstrate_services()
    demonstrate_reports()

    print("\n" + "=" * 60)
    print("✓ Все демонстрации завершены успешно!")
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
Основной модуль для запуска приложения.
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

from src.utils import load_transactions_from_excel
from src.views import get_home_page_data, get_events_page_data
from src.services import (
    profitable_cashback_categories,
    investment_bank,
    simple_search,
    search_by_phone_numbers,
    search_by_person_transfers
)
from src.reports import (
    spending_by_category,
    spending_by_weekday,
    spending_by_workday
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demonstrate_home_page() -> None:
    """Демонстрация работы главной страницы."""
    print("\n" + "="*50)
    print("ДЕМОНСТРАЦИЯ: ГЛАВНАЯ СТРАНИЦА")
    print("="*50)
    # Текущая дата для демонстрации
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Получаем данные для главной страницы
    home_data = get_home_page_data(current_date)
    
    # Выводим результат
    print(f"Приветствие: {home_data['greeting']}")
    print(f"Количество карт: {len(home_data['cards'])}")
    print(f"Курсы валют: {len(home_data['currency_rates'])}")
    print(f"Цены акций: {len(home_data['stock_prices'])}")
    
    # Сохраняем в файл для наглядности
    with open('home_page_demo.json', 'w', encoding='utf-8') as f:
        json.dump(home_data, f, ensure_ascii=False, indent=2)
    
    print("Данные сохранены в home_page_demo.json")
def demonstrate_services(transactions_df: pd.DataFrame) -> None:
    """Демонстрация работы сервисов."""
    print("\n" + "="*50)
    print("ДЕМОНСТРАЦИЯ: СЕРВИСЫ")
    print("="*50)
    
    # Конвертируем DataFrame в список словарей для сервисов
    transactions_list = transactions_df.to_dict('records')
    
    # 1. Выгодные категории кешбэка
    print("\n1. Выгодные категории повышенного кешбэка:")
    cashback_categories = profitable_cashback_categories(
        transactions_list,
        year=datetime.now().year,
        month=datetime.now().month
    )
    
    for category, amount in list(cashback_categories.items())[:5]:
        print(f"   {category}: {amount:.2f} руб.")
    # 2. Инвесткопилка
    print("\n2. Инвесткопилка:")
    savings = investment_bank(
        month=datetime.now().strftime("%Y-%m"),
        transactions=transactions_list,
        limit=50
    )
    print(f"   Сумма для инвесткопилки: {savings:.2f} руб.")
    
    # 3. Простой поиск
    print("\n3. Простой поиск (поиск 'оплата'):")
    search_results = simple_search("оплата", transactions_list)
    print(f"   Найдено транзакций: {len(search_results)}")
    
    # 4. Поиск по телефонным номерам
    print("\n4. Поиск по телефонным номерам:")
    phone_results = search_by_phone_numbers(transactions_list)
    print(f"   Найдено транзакций с телефонами: {len(phone_results)}")
    # 5. Поиск переводов физлицам
    print("\n5. Поиск переводов физическим лицам:")
    person_transfers = search_by_person_transfers(transactions_list)
    print(f"   Найдено переводов физлицам: {len(person_transfers)}")


def demonstrate_reports(transactions_df: pd.DataFrame) -> None:
    """Демонстрация работы отчетов."""
    print("\n" + "="*50)
    print("ДЕМОНСТРАЦИЯ: ОТЧЕТЫ")
    print("="*50)
    
    # 1. Траты по категории
    print("\n1. Траты по категории (пример с 'Супермаркеты'):")
    category_spending = spending_by_category(
        transactions_df,
        category="Супермаркеты"
    )
    if not category_spending.empty:
        print(category_spending.to_string())
    else:
        print("   Нет данных по указанной категории")
    
    # 2. Траты по дням недели
    print("\n2. Траты по дням недели:")
    weekday_spending = spending_by_weekday(transactions_df)
    
    if not weekday_spending.empty:
        print(weekday_spending.to_string())
    else:
        print("   Нет данных для анализа")
    
    # 3. Траты в рабочий/выходной день
    print("\n3. Траты в рабочий/выходной день:")
    workday_spending = spending_by_workday(transactions_df)
    if not workday_spending.empty:
        print(workday_spending.to_string())
    else:
        print("   Нет данных для анализа")


def main() -> None:
    """Основная функция приложения."""
    try:
        print("="*60)
        print("ПРИЛОЖЕНИЕ ДЛЯ АНАЛИЗА ТРАНЗАКЦИЙ")
        print("="*60)
        
        # Загружаем транзакции
        excel_file = "data/operations.xlsx"
        
        try:
            transactions_df = load_transactions_from_excel(excel_file)
            print(f"\n✓ Загружено {len(transactions_df)} транзакций из {excel_file}")
        except FileNotFoundError:
            print(f"\n⚠ Файл {excel_file} не найден. Создаем тестовые данные...")
            # Создаем тестовые данные для демонстрации
            transactions_df = pd.DataFrame({
                'Дата операции': pd.date_range('2024-01-01', periods=100, freq='D'),
                'Сумма платежа': [-100, -200, -300] * 33 + [1000],
                'Категория': ['Супермаркеты', 'Кафе', 'Транспорт'] * 33 + ['Пополнение'],
                'Описание': ['Покупка продуктов', 'Обед в кафе', 'Такси'] * 33 + ['Зарплата'],
                'Номер карты': ['1234'] * 100,
                'Статус': ['OK'] * 100,
                'Кешбэк': [1, 2, 0.5] * 33 + [0]
            })
            print("✓ Созданы тестовые данные (100 транзакций)")
        
        # Демонстрируем функциональность
        demonstrate_home_page()
        
        if not transactions_df.empty:
            demonstrate_services(transactions_df)
            demonstrate_reports(transactions_df)
        print("\n" + "="*60)
        print("РАБОТА ПРИЛОЖЕНИЯ ЗАВЕРШЕНА")
        print("="*60)
        print("\nСозданные файлы:")
        print("  • home_page_demo.json - данные главной страницы")
        print("  • report_*.json - отчеты (создаются автоматически)")
        
    except Exception as e:
        logger.error(f"Ошибка в работе приложения: {e}")
        print(f"\n❌ Произошла ошибка: {e}")


if __name__ == "__main__":
    main()

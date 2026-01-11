"""
Скрипт для запуска приложения Transaction Analyzer.
"""

import os
import sys

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Загружаем переменные окружения из .env
from dotenv import load_dotenv

load_dotenv()

from src.main import app, main

if __name__ == "__main__":
    print("=" * 50)
    print("Transaction Analyzer")
    print("=" * 50)
    print(f"API ключ валют: {'установлен' if os.environ.get('EXCHANGE_RATE_API_KEY') else 'не установлен'}")
    print(f"API ключ акций: {'установлен' if os.environ.get('STOCK_API_KEY') else 'не установлен'}")
    print()

    # Запускаем основную функцию для демонстрации
    result = main()
    print(f"\nРезультат: {result}")

    # Запускаем Flask приложение
    print("\nЗапуск веб-сервера на http://127.0.0.1:5000")
    print("Доступные endpoints:")
    print("  /         - Главная страница API")
    print("  /api/home - Данные главной страницы")
    print("  /api/events - Данные страницы событий")
    print("  /health   - Health check")
    print("=" * 50)

    app.run(debug=True, host='127.0.0.1', port=5000)
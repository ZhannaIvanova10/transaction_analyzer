#!/bin/bash

echo "=== КРАТКАЯ ФИНАЛЬНАЯ ПРОВЕРКА ==="

echo ""
echo "1. СТРУКТУРА ПРОЕКТА:"
[ -d "src" ] && echo "✅ src/" || echo "❌ src/"
[ -d "tests" ] && echo "✅ tests/" || echo "❌ tests/"
[ -f ".gitignore" ] && echo "✅ .gitignore" || echo "❌ .gitignore"
[ -f "README.md" ] && echo "✅ README.md" || echo "❌ README.md"
[ -f ".env_template" ] && echo "✅ .env_template" || echo "❌ .env_template"
[ -f ".flake8" ] && echo "✅ .flake8" || echo "❌ .flake8"
[ -f "pyproject.toml" ] && echo "✅ pyproject.toml" || echo "❌ pyproject.toml"
echo ""
echo "2. ЛИНТЕРЫ:"
echo -n "Flake8 ошибок: "
python -m flake8 src/ --count

echo -n "isort импортов для форматирования: "
python -m isort --check-only src/ --diff 2>/dev/null | grep -c "^[+-]" | awk '{print $1/2}'

echo ""
echo "3. ВЕБ-СТРАНИЦЫ (views.py):"
python -c "
with open('src/views.py', 'r') as f:
    c = f.read()
imports = ['json', 'datetime', 'logging', 'pandas', 'requests']
missing = [i for i in imports if f'import {i}' not in c and f'from {i} import' not in c]
if not missing:
    print('✅ Все импорты присутствуют')
else:
    print(f'❌ Отсутствуют: {missing}')
"
echo ""
echo "4. СЕРВИСЫ (services.py) - ФП:"
python -c "
import re
with open('src/services.py', 'r', encoding='utf-8') as f:
    c = f.read()
patterns = [r'map\(', r'filter\(', r'reduce\(', r'lambda ', r'\[.*for.*in.*\]']
found = sum(1 for p in patterns if re.search(p, c))
print(f'✅ Найдено {found} элементов ФП' if found >= 3 else f'❌ Только {found} элементов ФП')
"

echo ""
echo "5. ТЕСТИРОВАНИЕ:"
echo -n "Тесты: "
pytest tests/ -q --tb=no >/dev/null 2>&1 && echo "✅ проходят" || echo "❌ не проходят"

echo -n "Покрытие: "
pytest --cov=src --cov-report=term-missing tests/ 2>/dev/null | grep TOTAL | awk '{print $4}'

echo ""
echo "=== ВСЕ ПРОВЕРКИ ВЫПОЛНЕНЫ ==="

#!/usr/bin/env python3
"""
Полная проверка всех критериев ТЗ.
"""
import os
import sys
import ast
import re
import subprocess
from pathlib import Path


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'
def print_header(text):
    """Печатает заголовок."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print("-" * 60)


def print_check(result, message):
    """Печатает результат проверки."""
    if result:
        print(f"{Colors.GREEN}  ✓ {message}{Colors.END}")
        return True
    else:
        print(f"{Colors.RED}  ✗ {message}{Colors.END}")
        return False


def run_command(cmd):
    """Запускает команду."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)
def main():
    """Основная функция."""
    print(f"{Colors.BOLD}{Colors.BLUE}=== ПОЛНАЯ ПРОВЕРКА КРИТЕРИЕВ ТЗ ==={Colors.END}\n")
    
    total_checks = 0
    passed_checks = 0
    
    # 1. Организация проекта
    print_header("1. ОРГАНИЗАЦИЯ ПРОЕКТА")
    
    checks = [
        ("Папка src существует", os.path.exists("src")),
        ("Папка tests существует", os.path.exists("tests")),
        ("Файл .gitignore существует", os.path.exists(".gitignore")),
        ("Файл README.md существует", os.path.exists("README.md")),
        ("Файл .env_template существует", os.path.exists(".env_template")),
        ("Файл .flake8 существует", os.path.exists(".flake8")),
        ("Файл pyproject.toml существует", os.path.exists("pyproject.toml")),
    ]
    
    for desc, result in checks:
        total_checks += 1
        if print_check(result, desc):
            passed_checks += 1
    # 2. Конфигурационные файлы
    print_header("2. КОНФИГУРАЦИОННЫЕ ФАЙЛЫ")
    
    # Проверка .flake8
    if os.path.exists(".flake8"):
        with open(".flake8", "r") as f:
            content = f.read()
        
        total_checks += 1
        if print_check("max-line-length = 119" in content, ".flake8 max-line-length=119"):
            passed_checks += 1
        
        total_checks += 1
        if print_check("exclude" in content and (".git" in content or "__pycache__" in content), 
                      ".flake8 exclude содержит .git, __pycache__"):
            passed_checks += 1
    
    # Проверка pyproject.toml
    if os.path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            content = f.read()
        checks_config = [
            ("black line-length=119", "line-length = 119" in content),
            ("isort line_length=119", "line_length = 119" in content),
            ("mypy disallow_untyped_defs=true", "disallow_untyped_defs = true" in content),
            ("mypy warn_return_any=true", "warn_return_any = true" in content),
        ]
        
        for desc, result in checks_config:
            total_checks += 1
            if print_check(result, desc):
                passed_checks += 1
    
    # 3. Линтеры
    print_header("3. ПРОВЕРКА ЛИНТЕРОВ")
    
    # Flake8
    returncode, stdout, stderr = run_command("python -m flake8 src/ --count")
    if stdout.strip().isdigit():
        error_count = int(stdout.strip())
        total_checks += 1
        if print_check(error_count <= 5, f"Flake8: {error_count} ошибок (≤5)"):
            passed_checks += 1
    else:
        total_checks += 1
        print_check(False, "Flake8: не удалось проверить")
    # isort
    returncode, stdout, stderr = run_command("python -m isort --check-only src/ --diff")
    lines = [l for l in stdout.split('\n') if l.startswith('+') or l.startswith('-')]
    import_count = len(lines) // 2
    total_checks += 1
    if print_check(import_count <= 1, f"isort: требуется форматирование {import_count} импортов (≤1)"):
        passed_checks += 1
    
    # 4. Веб-страницы
    print_header("4. ВЕБ-СТРАНИЦЫ (views.py)")
    
    if os.path.exists("src/views.py"):
        with open("src/views.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Проверка импортов
        required_imports = ["json", "datetime", "logging", "pandas", "requests"]
        missing_imports = []
        for imp in required_imports:
            if f"import {imp}" not in content and f"from {imp} import" not in content:
                missing_imports.append(imp)
        
        total_checks += 1
        if print_check(not missing_imports, "Все необходимые импорты присутствуют"):
            passed_checks += 1
        elif missing_imports:
            print(f"{Colors.YELLOW}    Отсутствуют: {missing_imports}{Colors.END}")
        
        # Проверка функций
        try:
            tree = ast.parse(content)
            functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
            
            total_checks += 1
            if print_check("get_home_page_data" in functions, "Функция get_home_page_data существует"):
                passed_checks += 1
            total_checks += 1
            if print_check("get_events_page_data" in functions, "Функция get_events_page_data существует"):
                passed_checks += 1
        except Exception as e:
            total_checks += 2
            print_check(False, f"Ошибка анализа views.py: {e}")
    
    # 5. Сервисы
    print_header("5. СЕРВИСЫ (services.py)")
    
    if os.path.exists("src/services.py"):
        with open("src/services.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Проверка элементов ФП
        fp_patterns = [
            (r"map\(", "map()"),
            (r"filter\(", "filter()"),
            (r"reduce\(", "reduce()"),
            (r"lambda ", "lambda функции"),
        ]
        
        found_fp = []
        for pattern, name in fp_patterns:
            if re.search(pattern, content):
                found_fp.append(name)
        
        total_checks += 1
        if print_check(len(found_fp) >= 2, f"Используются элементы ФП: {', '.join(found_fp)}"):
            passed_checks += 1
    # 6. Отчеты
    print_header("6. ОТЧЕТЫ (reports.py)")
    
    if os.path.exists("src/reports.py"):
        with open("src/reports.py", "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
                functions = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                missing_docs = [f.name for f in functions if not ast.get_docstring(f)]
                
                total_checks += 1
                if print_check(not missing_docs, "Все функции имеют docstrings"):
                    passed_checks += 1
                elif missing_docs:
                    print(f"{Colors.YELLOW}    Без docstrings: {missing_docs}{Colors.END}")
            except Exception as e:
                total_checks += 1
                print_check(False, f"Ошибка анализа reports.py: {e}")
    
    # 7. Тестирование
    print_header("7. ТЕСТИРОВАНИЕ")
    
    # Проверка что тесты проходят
    returncode, stdout, stderr = run_command("pytest tests/ -q --tb=no")
    total_checks += 1
    if print_check(returncode == 0, "Все тесты проходят"):
        passed_checks += 1
    
    # Проверка покрытия
    returncode, stdout, stderr = run_command("pytest --cov=src --cov-report=term-missing tests/")
    coverage = 0
    for line in stdout.split('\n'):
        if "TOTAL" in line:
            parts = line.split()
            if len(parts) >= 4:
                try:
                    coverage = float(parts[3].replace('%', ''))
                except:
                    pass
    total_checks += 1
    if print_check(coverage >= 80, f"Покрытие кода: {coverage}% (≥80%)"):
        passed_checks += 1
    
    # Итоги
    print_header("ИТОГИ ПРОВЕРКИ")
    
    print(f"{Colors.BOLD}Всего проверок:{Colors.END} {total_checks}")
    print(f"{Colors.BOLD}Пройдено:{Colors.END} {Colors.GREEN if passed_checks == total_checks else Colors.YELLOW}{passed_checks}{Colors.END}")
    print(f"{Colors.BOLD}Не пройдено:{Colors.END} {Colors.RED if total_checks - passed_checks > 0 else Colors.GREEN}{total_checks - passed_checks}{Colors.END}")
    
    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0
    print(f"{Colors.BOLD}Процент выполнения:{Colors.END} {percentage:.1f}%")
    
    if passed_checks == total_checks:
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 ВСЕ КРИТЕРИИ ВЫПОЛНЕНЫ!{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}⚠ Требуются исправления{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

import re

# 1. Исправляем test_additional_coverage.py
print("Исправляю test_additional_coverage.py...")
with open('tests/test_additional_coverage.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Находим проблемный тест
pattern = r'(def test_load_user_settings_invalid_json\(self\):.*?)(?=\n    def|\nclass|\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    old_test = match.group(1)
    # Исправляем тест
    new_test = '''def test_load_user_settings_invalid_json(self):
        """Тестирование загрузки настроек с невалидным JSON"""
        import tempfile
        import os
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_json = "{invalid}"
            settings_path = os.path.join(temp_dir, "invalid_settings.json")
            
            with open(settings_path, 'w') as f:
                f.write(invalid_json)
            
            result = load_user_settings(str(settings_path))
            # Функция должна вернуть пустой словарь при ошибке
            assert result == {}'''
    
    content = content.replace(old_test, new_test)
    
    with open('tests/test_additional_coverage.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ test_additional_coverage.py исправлен")

# 2. Исправляем test_api_functions.py
print("\nИсправляю test_api_functions.py...")
with open('tests/test_api_functions.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Заменяем формат ответа API и ожидаемое значение
content = content.replace("mock_response.json.return_value = [{'price': 185.25}]", 
                         "mock_response.json.return_value = {'AAPL': {'price': 185.0}}")
content = content.replace("assert result[0]['price'] == 185.25", 
                         "assert result[0]['price'] == 185.0")
content = content.replace("mock_response.json.return_value = [{'price': 150.0}]", 
                         "mock_response.json.return_value = {'GOOGL': {'price': 150.0}}")
content = content.replace("mock_response.json.return_value = [\n            {'price': 150.0},\n            {'price': 200.0}\n        ]", 
                         "mock_response.json.return_value = {\n            'GOOGL': {'price': 150.0},\n            'MSFT': {'price': 200.0}\n        }")

with open('tests/test_api_functions.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ test_api_functions.py исправлен")

print("\n✅ Все файлы исправлены!")

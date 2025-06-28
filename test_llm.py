#!/usr/bin/env python
"""
Тестовый скрипт для проверки работы LLM сервиса
"""

import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archie.settings')
django.setup()

from archie.services.llm_service import LLMService
import tempfile

def test_llm_service():
    """Тестирует LLM сервис"""
    print("🧪 Тестирование LLM сервиса...")
    
    # Создаем тестовый файл
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
        ДОГОВОР КУПЛИ-ПРОДАЖИ
        
        г. Москва                                    01.01.2024
        
        ООО "Продавец", именуемое в дальнейшем "Продавец", в лице директора Иванова И.И., 
        действующего на основании Устава, с одной стороны, и ООО "Покупатель", именуемое 
        в дальнейшем "Покупатель", в лице директора Петрова П.П., действующего на основании 
        Устава, с другой стороны, заключили настоящий договор о нижеследующем:
        
        1. ПРЕДМЕТ ДОГОВОРА
        Продавец обязуется передать в собственность Покупателя товар, а Покупатель обязуется 
        принять товар и уплатить за него цену в размере 100 000 (сто тысяч) рублей.
        
        2. КАЧЕСТВО ТОВАРА
        Товар должен соответствовать требованиям ГОСТ и техническим условиям.
        
        3. СРОКИ ИСПОЛНЕНИЯ
        Товар должен быть передан в течение 10 дней с момента подписания договора.
        
        Подписи сторон:
        Продавец: _________________     Покупатель: _________________
        """)
        test_file_path = f.name
    
    try:
        # Тестируем LLM сервис
        llm_service = LLMService()
        
        print(f"📄 Анализируем файл: {test_file_path}")
        result = llm_service.analyze_document(test_file_path)
        
        print("\n✅ Результат анализа:")
        print(f"📝 Название: {result.get('title', 'Не определено')}")
        print(f"🏷️  Категория: {result.get('category', 'Не определена')}")
        print(f"📋 Описание: {result.get('description', 'Не определено')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return None
        
    finally:
        # Удаляем временный файл
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

if __name__ == "__main__":
    test_llm_service() 
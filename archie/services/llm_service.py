import os
import logging
from typing import Dict, Optional, Tuple
from django.conf import settings
import json

logger = logging.getLogger(__name__)

# Условный импорт openai
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI не установлен. LLM функции будут недоступны.")

# Условный импорт PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("Pillow не установлен. Обработка изображений будет ограничена.")


class LLMService:
    """Сервис для работы с LLM для анализа документов"""
    
    def __init__(self):
        """Инициализация сервиса LLM"""
        self.api_key = settings.OPENAI_API_KEY
        self.client = None
        
        if not self.api_key:
            logger.warning("OPENAI_API_KEY не настроен")
            return
            
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI не установлен")
            return
            
        try:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Ошибка инициализации OpenAI клиента: {e}")
    
    def analyze_document(
        self, 
        file_path: str, 
        file_content: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Анализирует документ и генерирует название, категорию и описание
        
        Args:
            file_path: Путь к файлу документа
            file_content: Текстовое содержимое файла (если доступно)
            
        Returns:
            Словарь с полями: title, category, description
        """
        try:
            if not self.api_key or not self.client:
                logger.warning("LLM недоступен - OPENAI_API_KEY не настроен или клиент не инициализирован")
                return self._get_default_values()
            
            # Определяем тип файла
            file_type = self._get_file_type(file_path)
            
            # Получаем содержимое файла
            content = file_content or self._extract_content(file_path, file_type)
            
            if not content:
                logger.warning("Не удалось извлечь содержимое файла")
                return self._get_default_values()
            
            # Анализируем с помощью LLM
            return self._analyze_with_llm(content, file_type)
            
        except Exception as e:
            logger.error(f"Ошибка при анализе документа: {e}")
            return self._get_default_values()
    
    def _get_file_type(self, file_path: str) -> str:
        """Определяет тип файла по расширению"""
        ext = file_path.lower().split('.')[-1]
        mime_map = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        return mime_map.get(ext, 'application/octet-stream')
    
    def _extract_content(self, file_path: str, file_type: str) -> Optional[str]:
        """Извлекает текстовое содержимое из файла"""
        try:
            if file_type.startswith('image/'):
                return self._extract_text_from_image(file_path)
            elif file_type == 'text/plain':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_type == 'application/pdf':
                return self._extract_text_from_pdf(file_path)
            else:
                logger.warning(f"Неподдерживаемый тип файла: {file_type}")
                return None
        except Exception as e:
            logger.error(f"Ошибка при извлечении содержимого: {e}")
            return None
    
    def _extract_text_from_image(self, file_path: str) -> Optional[str]:
        """Извлекает текст из изображения с помощью OCR"""
        try:
            if not PIL_AVAILABLE:
                logger.warning("Pillow не установлен, невозможно обработать изображение")
                return f"Изображение: {os.path.basename(file_path)}"
            
            if not self.client:
                logger.warning("OpenAI клиент недоступен")
                return f"Изображение: {os.path.basename(file_path)}"
            
            # Отправляем изображение в OpenAI Vision API
            with open(file_path, "rb") as image_file:
                response = self.client.chat.completions.create(
                    model="gpt-4-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Извлеки весь текст из этого изображения. Если это документ, опиши его тип и основное содержимое."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{image_file.read()}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=1000
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из изображения: {e}")
            return f"Изображение: {os.path.basename(file_path)}"
    
    def _extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        """Извлекает текст из PDF файла"""
        try:
            # В реальном проекте здесь можно использовать PyPDF2 или pdfplumber
            # Для простоты возвращаем базовую информацию
            return f"PDF документ: {os.path.basename(file_path)}"
        except Exception as e:
            logger.error(f"Ошибка при извлечении текста из PDF: {e}")
            return None
    
    def _analyze_with_llm(self, content: str, file_type: str) -> Dict[str, str]:
        """Анализирует содержимое с помощью LLM"""
        try:
            if not self.client:
                logger.warning("OpenAI клиент недоступен")
                return self._get_default_values()
            
            prompt = f"""
            Проанализируй следующий документ и создай:
            1. Краткое и информативное название (до 50 символов)
            2. Подходящую категорию (например: Договоры, Счета, Документы, Отчеты, Письма)
            3. Краткое описание (до 200 символов)
            
            Тип файла: {file_type}
            Содержимое: {content[:2000]}  # Ограничиваем для экономии токенов
            
            Ответь в формате JSON:
            {{
                "title": "название документа",
                "category": "категория",
                "description": "описание документа"
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Ты помощник для анализа документов. Отвечай только в формате JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Парсим JSON ответ
            response_content = response.choices[0].message.content
            if response_content:
                result = json.loads(response_content)
                logger.info(f"LLM анализ завершен: {result}")
                return result
            else:
                logger.warning("Пустой ответ от LLM")
                return self._get_default_values()
            
        except Exception as e:
            logger.error(f"Ошибка при анализе с LLM: {e}")
            return self._get_default_values()
    
    def _get_default_values(self) -> Dict[str, str]:
        """Возвращает значения по умолчанию"""
        return {
            "title": "Новый документ",
            "category": "Документы",
            "description": "Документ загружен в систему Archie"
        } 
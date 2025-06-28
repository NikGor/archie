from django import forms
from .models import Document
import logging

logger = logging.getLogger(__name__)

# Условный импорт LLMService
try:
    from archie.services.llm_service import LLMService
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("LLM сервис недоступен. Автогенерация полей будет отключена.")


class DocumentForm(forms.ModelForm):
    """Форма для загрузки документов с автоматической генерацией полей через LLM"""
    
    # Добавляем поле для автоматической генерации
    auto_generate = forms.BooleanField(
        required=False,
        initial=True,
        label="Автоматически сгенерировать название, категорию и описание",
        help_text="Использовать ИИ для анализа документа"
    )
    
    class Meta:
        model = Document
        fields = ('title', 'text', 'scan', 'category')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название документа или оставьте пустым для автогенерации',
                'required': False
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Добавьте описание документа или оставьте пустым для автогенерации...',
                'rows': 4
            }),
            'scan': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png'
            }),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Договоры, Счета, Документы или оставьте пустым для автогенерации',
                'required': False
            })
        }
        labels = {
            'title': 'Название документа',
            'text': 'Описание',
            'scan': 'Файл документа',
            'category': 'Категория'
        }
        help_texts = {
            'title': 'Краткое и понятное название документа (автогенерируется, если оставить пустым)',
            'text': 'Дополнительная информация о документе (автогенерируется, если оставить пустым)',
            'scan': 'Поддерживаемые форматы: PDF, DOC, DOCX, TXT, JPG, PNG',
            'category': 'Категория для организации документов (автогенерируется, если оставить пустым)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля необязательными, так как они могут быть сгенерированы автоматически
        self.fields['title'].required = False
        self.fields['category'].required = False
        self.fields['text'].required = False
        
        # Если LLM недоступен, отключаем автогенерацию
        if not LLM_AVAILABLE:
            self.fields['auto_generate'].initial = False
            self.fields['auto_generate'].help_text = "ИИ недоступен. Заполните поля вручную."
    
    def clean(self):
        """Валидация формы с автоматической генерацией полей"""
        cleaned_data = super().clean()
        
        # Проверяем, есть ли файл
        scan_file = cleaned_data.get('scan')
        if not scan_file:
            raise forms.ValidationError("Файл документа обязателен")
        
        # Если включена автогенерация и LLM доступен, генерируем поля
        auto_generate = cleaned_data.get('auto_generate', True)
        
        if auto_generate and LLM_AVAILABLE:
            try:
                # Создаем временный файл для анализа
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(scan_file.name)[1]) as temp_file:
                    for chunk in scan_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                try:
                    # Анализируем документ с помощью LLM
                    llm_service = LLMService()
                    analysis_result = llm_service.analyze_document(temp_file_path)
                    
                    # Заполняем пустые поля результатами анализа
                    if not cleaned_data.get('title'):
                        cleaned_data['title'] = analysis_result.get('title', 'Новый документ')
                    
                    if not cleaned_data.get('category'):
                        cleaned_data['category'] = analysis_result.get('category', 'Документы')
                    
                    if not cleaned_data.get('text'):
                        cleaned_data['text'] = analysis_result.get('description', 'Документ загружен в систему Archie')
                    
                    logger.info(f"Автогенерация полей завершена: {analysis_result}")
                    
                finally:
                    # Удаляем временный файл
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                        
            except Exception as e:
                logger.error(f"Ошибка при автогенерации полей: {e}")
                # Если автогенерация не удалась, используем значения по умолчанию
                if not cleaned_data.get('title'):
                    cleaned_data['title'] = f"Документ {scan_file.name}"
                if not cleaned_data.get('category'):
                    cleaned_data['category'] = 'Документы'
                if not cleaned_data.get('text'):
                    cleaned_data['text'] = f'Документ "{scan_file.name}" загружен в систему Archie'
        else:
            # Если автогенерация отключена или LLM недоступен, используем значения по умолчанию
            if not cleaned_data.get('title'):
                cleaned_data['title'] = f"Документ {scan_file.name}"
            if not cleaned_data.get('category'):
                cleaned_data['category'] = 'Документы'
            if not cleaned_data.get('text'):
                cleaned_data['text'] = f'Документ "{scan_file.name}" загружен в систему Archie'
        
        # Проверяем, что у нас есть все необходимые поля
        if not cleaned_data.get('title'):
            raise forms.ValidationError("Название документа обязательно")
        
        if not cleaned_data.get('category'):
            raise forms.ValidationError("Категория документа обязательна")
        
        return cleaned_data

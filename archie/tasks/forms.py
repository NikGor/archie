from django import forms
from .models import ScanSession, Task


class ScanSessionForm(forms.ModelForm):
    """Форма для создания сессии сканирования"""
    
    class Meta:
        model = ScanSession
        fields = ['title', 'scanner_name', 'resolution']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название документа (опционально)'
            }),
            'scanner_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя сканера (оставьте пустым для автовыбора)'
            }),
            'resolution': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 72,
                'max': 1200,
                'step': 1
            })
        }
        labels = {
            'title': 'Название документа',
            'scanner_name': 'Имя сканера',
            'resolution': 'Разрешение (DPI)'
        }
        help_texts = {
            'title': 'Название будет сгенерировано автоматически, если оставить пустым',
            'scanner_name': 'Оставьте пустым для автоматического выбора первого доступного сканера',
            'resolution': 'Рекомендуется 300 DPI для документов, 600 DPI для изображений'
        }

class TaskForm(forms.ModelForm):
    """Форма для создания и редактирования задач"""
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'type',
            'status',
            'document',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название задачи'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'document': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'type': 'Тип задачи',
            'status': 'Статус',
            'document': 'Документ',
        } 
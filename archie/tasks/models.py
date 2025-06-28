from django.db import models
from django.utils import timezone
from archie.documents.models import Document
import logging

logger = logging.getLogger(__name__)

class Task(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новая'
        IN_PROGRESS = 'in_progress', 'В процессе'
        DONE = 'done', 'Завершена'
        ERROR = 'error', 'Ошибка'

    class Type(models.TextChoices):
        SCAN = 'scan', 'Сканирование'
        OCR = 'ocr', 'Распознавание'
        SEND = 'send', 'Отправка'
        CUSTOM = 'custom', 'Другое'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )
    type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.CUSTOM
    )
    completed = models.BooleanField(default=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks'
    )
    result = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title} ({self.get_status_display()})'


class ScanSession(models.Model):
    """Модель для сессии сканирования"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('scanning', 'Сканирование'),
        ('processing', 'Обработка'),
        ('completed', 'Завершено'),
        ('failed', 'Ошибка'),
    ]
    
    title = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scanner_name = models.CharField(max_length=100, blank=True)
    resolution = models.IntegerField(default=300, help_text="Разрешение в DPI")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Связь с документом после обработки
    document = models.ForeignKey('documents.Document', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Сканирование {self.id}: {self.title or 'Без названия'}"
    
    def complete(self, document=None):
        """Завершает сессию сканирования"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if document:
            self.document = document
        self.save()
    
    def fail(self, error_message):
        """Отмечает сессию как неудачную"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()

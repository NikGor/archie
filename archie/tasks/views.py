from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Task, ScanSession
from .forms import ScanSessionForm, TaskForm
import logging

logger = logging.getLogger(__name__)


class TaskListView(ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    ordering = ['-created_at']


class TaskDetailView(DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'
    context_object_name = 'task'


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        logger.info('Создание новой задачи')
        messages.success(self.request, 'Задача успешно создана')
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.info('Ошибка при создании задачи')
        messages.error(self.request, 'Ошибка при создании задачи')
        return super().form_invalid(form)


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        logger.info('Обновление задачи')
        messages.success(self.request, 'Задача успешно обновлена')
        return super().form_valid(form)

    def form_invalid(self, form):
        logger.info('Ошибка при обновлении задачи')
        messages.error(self.request, 'Ошибка при обновлении задачи')
        return super().form_invalid(form)


class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'
    success_url = reverse_lazy('tasks')

    def delete(self, request, *args, **kwargs):
        logger.info('Удаление задачи')
        messages.success(self.request, 'Задача удалена')
        return super().delete(request, *args, **kwargs)


class ScanListView(ListView):
    """Список сессий сканирования"""
    model = ScanSession
    template_name = 'tasks/scan_list.html'
    context_object_name = 'scan_sessions'
    ordering = ['-created_at']


class ScanCreateView(CreateView):
    """Создание новой сессии сканирования"""
    model = ScanSession
    form_class = ScanSessionForm
    template_name = 'tasks/scan_create.html'
    success_url = reverse_lazy('scan_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Сессия сканирования создана')
        return response


class ScanDetailView(DetailView):
    """Детали сессии сканирования"""
    model = ScanSession
    template_name = 'tasks/scan_detail.html'
    context_object_name = 'scan_session'


class ScanExecuteView(View):
    """Выполнение сканирования"""
    
    def post(self, request, pk):
        scan_session = get_object_or_404(ScanSession, pk=pk)
        
        try:
            # Импортируем сканер
            from scan_documents import DocumentScanner
            
            # Обновляем статус
            scan_session.status = 'scanning'
            scan_session.save()
            
            # Выполняем сканирование
            scanner = DocumentScanner()
            scanned_file = scanner.scan_document(
                scanner_name=scan_session.scanner_name or None,
                resolution=scan_session.resolution
            )
            
            if scanned_file:
                # Обновляем статус на обработку
                scan_session.status = 'processing'
                scan_session.save()
                
                # Обрабатываем документ
                document = scanner.process_scanned_document(
                    scanned_file,
                    title=scan_session.title or None
                )
                
                if document:
                    # Завершаем сессию
                    scan_session.complete(document)
                    messages.success(request, f'Документ успешно отсканирован: {document.title}')
                    return JsonResponse({
                        'status': 'success',
                        'message': f'Документ отсканирован: {document.title}',
                        'document_id': document.id
                    })
                else:
                    scan_session.fail("Ошибка при обработке документа")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Ошибка при обработке документа'
                    })
            else:
                scan_session.fail("Ошибка при сканировании")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Ошибка при сканировании'
                })
                
        except Exception as e:
            logger.error(f"Ошибка при сканировании: {e}")
            scan_session.fail(str(e))
            return JsonResponse({
                'status': 'error',
                'message': f'Ошибка: {str(e)}'
            })


class ScanStatusView(View):
    """Получение статуса сканирования"""
    
    def get(self, request, pk):
        scan_session = get_object_or_404(ScanSession, pk=pk)
        return JsonResponse({
            'status': scan_session.status,
            'message': scan_session.error_message or '',
            'document_id': scan_session.document.id if scan_session.document else None
        })


class ScannerListView(View):
    """Получение списка доступных сканеров"""
    
    def get(self, request):
        try:
            from scan_documents import DocumentScanner
            
            scanner = DocumentScanner()
            scanners = []
            
            # Проверяем SANE сканеры
            try:
                import subprocess
                result = subprocess.run(['scanimage', '--list-devices'], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'device' in line.lower():
                            # Парсим строку вида "device `scanner_name' is a `scanner_type'"
                            parts = line.split("'")
                            if len(parts) >= 3:
                                scanner_name = parts[1]
                                scanner_type = parts[3] if len(parts) > 3 else 'Unknown'
                                scanners.append({
                                    'name': scanner_name,
                                    'type': scanner_type,
                                    'platform': 'SANE'
                                })
            except Exception as e:
                logger.warning(f"Ошибка при получении SANE сканеров: {e}")
            
            # Проверяем Windows WIA сканеры
            try:
                import win32com.client
                wia = win32com.client.Dispatch('WIA.DeviceManager')
                devices = wia.DeviceInfos
                for device in devices:
                    if device.Type == 1:  # Scanner device
                        scanners.append({
                            'name': device.Properties('Name').Value,
                            'type': 'WIA Scanner',
                            'platform': 'Windows'
                        })
            except ImportError:
                pass
            except Exception as e:
                logger.warning(f"Ошибка при получении WIA сканеров: {e}")
            
            # Проверяем macOS сканеры
            import sys
            if sys.platform == "darwin":
                try:
                    import subprocess
                    result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                                          capture_output=True, text=True)
                    if "scanner" in result.stdout.lower():
                        scanners.append({
                            'name': 'macOS Scanner',
                            'type': 'Image Capture',
                            'platform': 'macOS'
                        })
                except Exception as e:
                    logger.warning(f"Ошибка при получении macOS сканеров: {e}")
            
            return JsonResponse({
                'scanners': scanners,
                'count': len(scanners)
            })
            
        except Exception as e:
            logger.error(f"Ошибка при получении списка сканеров: {e}")
            return JsonResponse({
                'scanners': [],
                'count': 0,
                'error': str(e)
            })

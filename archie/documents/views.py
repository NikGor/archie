from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.contrib import messages
from .models import Document
from .forms import DocumentForm
import logging

logger = logging.getLogger(__name__)


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/index.html'
    context_object_name = 'documents'
    ordering = ['-date']
    paginate_by = 12
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем уникальные категории для фильтра
        context['categories'] = Document.objects.values_list('category', flat=True).distinct()
        return context


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/detail.html'
    context_object_name = 'document'

    def get(self, request, *args, **kwargs):
        logger.info(f"Viewing document details for document ID {kwargs['pk']}")
        return super().get(request, *args, **kwargs)


class DocumentUploadView(View):
    def get(self, request):
        form = DocumentForm()
        logger.info("Accessed document upload form")
        return render(request, 'documents/new.html', {'form': form})

    def post(self, request):
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Документ успешно загружен')
            return redirect('documents')
        return render(request, 'documents/new.html', {'form': form})


class DocumentDeleteView(View):
    def post(self, request, pk):
        try:
            document = get_object_or_404(Document, pk=pk)
            document.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Ошибка при удалении документа {pk}: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

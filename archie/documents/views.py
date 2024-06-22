from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from .models import Document
from .forms import DocumentForm


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/index.html'
    context_object_name = 'documents'


class DocumentUploadView(View):
    def get(self, request):
        form = DocumentForm()
        return render(request, 'documents/new.html', {'form': form})

    def post(self, request):
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('documents')
        return render(request, 'documents/new.html', {'form': form})

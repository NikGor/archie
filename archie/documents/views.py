import logging
import os
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.contrib import messages
from .models import Document
from .forms import DocumentForm
from .tools import analyze_document_with_gpt, extract_text_from_pdf
from .. import settings


class DocumentListView(ListView):
    model = Document
    template_name = 'documents/index.html'
    context_object_name = 'documents'

    def get(self, request, *args, **kwargs):
        logging.info("Viewing document list")
        return super().get(request, *args, **kwargs)


class DocumentUploadView(View):
    def get(self, request):
        form = DocumentForm()
        logging.info("Accessed document upload form")
        return render(request, 'documents/new.html', {'form': form})

    def post(self, request):
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                document = form.save(commit=False)
                document.save()
                pdf_path = document.scan.path
                full_pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_path)
                logging.info(f"PDF path: {full_pdf_path}")

                if not os.path.exists(full_pdf_path):
                    logging.error(f"File does not exist: {full_pdf_path}")
                    messages.error(request, 'File does not exist.')
                    return render(request, 'documents/new.html', {'form': form})

                document_text = extract_text_from_pdf(full_pdf_path)
                analysis_results = analyze_document_with_gpt(document_text)

                if analysis_results:
                    document.title = analysis_results.get('title', '')
                    document.date = analysis_results.get('date', document.date)
                    document.category = analysis_results.get('category', document.category)
                    document.organization = analysis_results.get('organization', '')
                    document.text = analysis_results.get('text', '')
                    document.save()

                messages.success(request, 'Document uploaded and processed successfully.')
                return redirect('documents')
            except Exception as e:
                logging.error(f"Error processing document: {e}")
                messages.error(request, 'An error occurred while processing the document.')
                return render(request, 'documents/new.html', {'form': form})
        else:
            logging.warning("Invalid form submission")
            messages.error(request, 'Form is not valid.')
            return render(request, 'documents/new.html', {'form': form})


class DocumentDetailView(DetailView):
    model = Document
    template_name = 'documents/show.html'
    context_object_name = 'document'

    def get(self, request, *args, **kwargs):
        logging.info(f"Viewing document details for document ID {kwargs['pk']}")
        return super().get(request, *args, **kwargs)


class DocumentUpdateView(UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'documents/edit.html'
    success_url = reverse_lazy('documents')

    def form_valid(self, form):
        logging.info(f"Updating document ID {self.object.pk}")
        messages.success(self.request, 'Document updated successfully.')
        return super().form_valid(form)

    def form_invalid(self, form):
        logging.warning("Invalid form submission for document update")
        messages.error(self.request, 'Form is not valid.')
        return super().form_invalid(form)


class DocumentDeleteView(DeleteView):
    model = Document
    success_url = reverse_lazy('documents')

    def delete(self, request, *args, **kwargs):
        logging.info(f"Deleting document ID {kwargs['pk']}")
        messages.success(request, 'Document deleted successfully.')
        return super().delete(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logging.info(f"Redirecting to document list from delete view for document ID {kwargs['pk']}")
        return redirect('documents')

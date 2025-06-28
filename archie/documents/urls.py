from django.urls import path
from .views import DocumentListView, DocumentUploadView, DocumentDetailView, DocumentDeleteView

urlpatterns = [
    path('', DocumentListView.as_view(), name='documents'),
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('<int:pk>/delete/', DocumentDeleteView.as_view(), name='document_delete'),
]

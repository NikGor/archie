from django.urls import path, include
from .views import (DocumentListView,
                    DocumentUploadView,
                    DocumentDetailView,
                    DocumentUpdateView,
                    DocumentDeleteView)

urlpatterns = [
    path('', DocumentListView.as_view(), name='documents'),
    path('upload/', DocumentUploadView.as_view(), name='upload'),
    path('documents/<int:pk>/', DocumentDetailView.as_view(), name='show_document'),
    path('documents/<int:pk>/edit/', DocumentUpdateView.as_view(), name='edit_document'),
    path('documents/<int:pk>/delete/', DocumentDeleteView.as_view(), name='delete_document'),
]

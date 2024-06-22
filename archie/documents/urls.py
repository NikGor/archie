from django.urls import path
from .views import DocumentListView, DocumentUploadView

urlpatterns = [
    path('', DocumentListView.as_view(), name='documents'),
    path('upload/', DocumentUploadView.as_view(), name='upload'),
]

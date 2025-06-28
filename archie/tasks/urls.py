from django.urls import path
from .views import (
    TaskListView, TaskDetailView, TaskCreateView, TaskUpdateView, TaskDeleteView,
    ScanListView, ScanCreateView, ScanDetailView, ScanExecuteView, ScanStatusView, ScannerListView
)

urlpatterns = [
    path('', TaskListView.as_view(), name='tasks'),
    path('create/', TaskCreateView.as_view(), name='task_create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('<int:pk>/edit/', TaskUpdateView.as_view(), name='task_edit'),
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='task_delete'),
    path('scan/', ScanListView.as_view(), name='scan_list'),
    path('scan/create/', ScanCreateView.as_view(), name='scan_create'),
    path('scan/<int:pk>/', ScanDetailView.as_view(), name='scan_detail'),
    path('scan/<int:pk>/execute/', ScanExecuteView.as_view(), name='scan_execute'),
    path('scan/<int:pk>/status/', ScanStatusView.as_view(), name='scan_status'),
    path('scan/scanners/', ScannerListView.as_view(), name='scanner_list'),
]

from django.contrib import admin
from django.urls import path, include
from archie.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('documents/', include('archie.documents.urls')),
    path('tasks/', include('archie.tasks.urls')),
]

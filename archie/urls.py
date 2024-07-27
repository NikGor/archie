from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from archie.views import IndexView
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('documents/', include('archie.documents.urls')),
    path('tasks/', include('archie.tasks.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

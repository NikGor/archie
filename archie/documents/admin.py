from django.contrib import admin
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'category')
    list_filter = ('date', 'category')
    search_fields = ('title', 'text')

"""
Custom template filters for document management
"""
from django import template
import os

register = template.Library()


@register.filter
def filename(value):
    """
    Extract filename from file path
    """
    if not value:
        return ''
    return os.path.basename(str(value))


@register.filter
def file_extension(value):
    """
    Extract file extension from filename
    """
    if not value:
        return ''
    name = str(value)
    if '.' in name:
        return name.split('.')[-1].upper()
    return ''


@register.filter
def is_pdf(value):
    """
    Check if file is PDF
    """
    if not value:
        return False
    return str(value).lower().endswith('.pdf')


@register.filter
def is_image(value):
    """
    Check if file is an image
    """
    if not value:
        return False
    name = str(value).lower()
    return any(name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp'])


@register.filter
def truncate_filename(value, length=30):
    """
    Truncate filename to specified length
    """
    if not value:
        return ''
    name = str(value)
    if len(name) <= length:
        return name
    # length-3 (для троеточия), +1 чтобы срез был корректным
    return '...' + name[-(length-3+1):] 
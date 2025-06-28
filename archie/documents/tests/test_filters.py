"""
Tests for custom document filters
"""
from django.test import TestCase
from django.template import Template, Context
from django.template.loader import get_template


class DocumentFiltersTestCase(TestCase):
    """Test cases for custom document filters"""

    def test_filename_filter(self):
        """Test filename filter"""
        template = Template(
            '{% load document_filters %}'
            '{{ file_path|filename }}'
        )
        context = Context({'file_path': '/path/to/document.pdf'})
        self.assertEqual(template.render(context), 'document.pdf')

    def test_file_extension_filter(self):
        """Test file_extension filter"""
        template = Template(
            '{% load document_filters %}'
            '{{ file_path|file_extension }}'
        )
        context = Context({'file_path': 'document.pdf'})
        self.assertEqual(template.render(context), 'PDF')

    def test_is_pdf_filter(self):
        """Test is_pdf filter"""
        template = Template(
            '{% load document_filters %}'
            '{% if file_path|is_pdf %}PDF{% else %}NOT_PDF{% endif %}'
        )
        context = Context({'file_path': 'document.pdf'})
        self.assertEqual(template.render(context), 'PDF')

    def test_is_image_filter(self):
        """Test is_image filter"""
        template = Template(
            '{% load document_filters %}'
            '{% if file_path|is_image %}IMAGE{% else %}NOT_IMAGE{% endif %}'
        )
        context = Context({'file_path': 'image.jpg'})
        self.assertEqual(template.render(context), 'IMAGE')

    def test_truncate_filename_filter(self):
        """Test truncate_filename filter"""
        template = Template(
            '{% load document_filters %}'
            '{{ file_path|truncate_filename:10 }}'
        )
        context = Context({'file_path': 'very_long_filename.pdf'})
        self.assertEqual(template.render(context), '...name.pdf') 
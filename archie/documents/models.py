from django.db import models


class Document(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField(auto_now_add=True, blank=True)
    text = models.TextField(blank=True, null=True)
    scan = models.FileField(upload_to='documents/%Y/%m/%d/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title if self.title else "Document"

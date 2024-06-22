from django.db import models


class Document(models.Model):
    date = models.DateField(auto_now_add=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    scan = models.FileField(upload_to='documents/%Y/%m/%d/')
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.title

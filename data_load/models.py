from django.db import models
from datetime import datetime

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    synopsis = models.TextField(null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    score = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    url = models.URLField(unique=True)
    image = models.URLField(null=True)
    source = models.CharField(max_length=32)
    categories = models.TextField(null=True)
    isbn = models.IntegerField(null=True)
    last_updated = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.title} - {self.author}"

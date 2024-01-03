from django.db import models
from datetime import datetime

# Create your models here.
class Category(models.Model):
    url = models.URLField(unique=True)
    name = models.CharField(max_length=255)
    last_updated = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.name}"

class Book(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255, null=True)
    author = models.CharField(max_length=255, null=True)
    synopsis = models.TextField(null=True)
    score = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    image = models.URLField(null=True)
    categories = models.ManyToManyField(Category)
    bookBrowseID = models.IntegerField(null=True)
    last_updated = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.title} - {self.author}"
    
class Reviewer(models.Model):
    url = models.URLField(unique=True)
    name = models.CharField(max_length=255)
    bio = models.TextField()
    last_updated = models.DateTimeField(default=datetime.now)
    bookBrowseID = models.IntegerField(null=True)
    def __str__(self):
        return f"{self.bookBrowseID} - {self.name}"

class Review(models.Model):
    url = models.URLField(unique=True)
    text = models.TextField(null=True)
    score = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    last_updated = models.DateTimeField(default=datetime.now)
    reviewer = models.ForeignKey(Reviewer, null=True, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, null=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.reviewer != None and self.reviewer.name:
            return f"Review {self.id} by {self.reviewer.name}"
        return f"Review {self.id}"

class Alike(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='similar_to')
    similarities = models.ManyToManyField(Book)
from django.db import models

class Comment(models.Model):
    month = models.IntegerField()
    name = models.CharField(max_length=20)
    score = models.IntegerField()
    content = models.TextField()

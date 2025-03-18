from django.db import models

# Create your models here.
class Ads(models.Model):
    content = models.CharField(max_length=1000)


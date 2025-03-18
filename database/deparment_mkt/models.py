from django.db import models

# Create your models here.
class DepartmentMkt(models.Model):
    name = models.CharField(max_length=100)
    salary = models.FloatField()

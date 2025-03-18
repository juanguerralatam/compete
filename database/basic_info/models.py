from django.db import models

# Create your models here.
class BasicInfo(models.Model):
    brand = models.CharField(max_length=100)
    fix_cost = models.IntegerField(default=0)
    variable_cost = models.IntegerField(default=0)
    capital = models.IntegerField(default=0)

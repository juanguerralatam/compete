from django.db import models

# Create your models here.
class Operations(models.Model):
    income = models.IntegerField(default=0)
    expenses = models.IntegerField(default=0)
    salary_rd = models.IntegerField(default=0)
    salary_maketing = models.IntegerField(default=0)
    score_product = models.FloatField(default=0)
    score_add = models.FloatField(default=0)
    rival_info = models.TextField()

from rest_framework import serializers
from .models import Operations

class OperationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operations
        fields = ['id', 'income', 'expenses', 'salary_rd', 'salary_maketing', 'score_product', 'score_add', 'rival_info']
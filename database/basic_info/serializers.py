from rest_framework import serializers
from .models import BasicInfo

class BasicInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicInfo
        fields = ['id', 'brand', 'fix_cost', 'variable_cost', 'capital']
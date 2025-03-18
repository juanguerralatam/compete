from rest_framework import serializers
from .models import DepartmentRD

class DepartmentRDSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentRD
        fields = ['id', 'name', 'salary']
        
    def validate_salary(self, value):
        if value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value
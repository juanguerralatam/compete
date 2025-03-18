from rest_framework import serializers
from .models import DepartmentMkt

class DepartmentMktSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentMkt
        fields = ['id', 'name', 'salary']
        
    def validate_salary(self, value):
        if value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value
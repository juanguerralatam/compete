from django.http import JsonResponse
from rest_framework import viewsets, response
from django_filters.rest_framework import DjangoFilterBackend
from utils.helpers import convert_to_string_format

from .models import DepartmentRD
from .serializers import DepartmentRD

class DepartmentRDViewSet(viewsets.ModelViewSet):
    queryset = DepartmentRD.objects.all()
    serializer_class = DepartmentRD
    filter_backends = [DjangoFilterBackend]
    filter_fields = "__all__"
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        _string = convert_to_string_format(serializer.data)
        return response.Response(_string, content_type='text/plain')
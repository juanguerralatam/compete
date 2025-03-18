from django.http import JsonResponse
from rest_framework import viewsets, response
from django_filters.rest_framework import DjangoFilterBackend
from utils.helpers import convert_to_string_format

from .models import DepartmentMkt
from .serializers import DepartmentMkt

class DepartmentMktViewSet(viewsets.ModelViewSet):
    queryset = DepartmentMkt.objects.all()
    serializer_class = DepartmentMkt
    filter_backends = [DjangoFilterBackend]
    filter_fields = "__all__"
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        _string = convert_to_string_format(serializer.data)
        return response.Response(_string, content_type='text/plain')
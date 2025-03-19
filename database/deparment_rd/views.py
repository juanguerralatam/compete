from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import DepartmentRD
from .serializers import DepartmentRDSerializer

class DepartmentRDListView(generics.ListCreateAPIView):
    queryset = DepartmentRD.objects.all()
    serializer_class = DepartmentRDSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = '__all__'

class DepartmentRDDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DepartmentRD.objects.all()
    serializer_class = DepartmentRDSerializer

def Show(request):
    try:
        department_rd = DepartmentRD.objects.first()
        if department_rd:
            data = {
                'brand': department_rd.brand,
                'fix_cost': department_rd.fix_cost,
                'variable_cost': department_rd.variable_cost,
                'capital': department_rd.capital
            }
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'error': 'No DepartmentRD data found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
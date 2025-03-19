from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from .models import DepartmentRD
from .serializers import DepartmentRDSerializer

class DepartmentRDListView(generics.ListCreateAPIView):
    queryset = DepartmentRD.objects.all()
    serializer_class = DepartmentRDSerializer

class DepartmentRDDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DepartmentRD.objects.all()
    serializer_class = DepartmentRDSerializer

def Show(request):
    try:
        # Get the department RD info
        department_rd = DepartmentRD.objects.first()
        department_data = DepartmentRDSerializer(department_rd).data if department_rd else None

        if not department_data:
            return JsonResponse({'error': 'No DepartmentRD data found'}, status=404)

        data = {
            'department': department_data
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
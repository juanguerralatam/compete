from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Avg
from .models import DepartmentMkt
from .serializers import DepartmentMktSerializer
from comment.models import Comment

class DepartmentMktListView(generics.ListCreateAPIView):
    queryset = DepartmentMkt.objects.all()
    serializer_class = DepartmentMktSerializer

class DepartmentMktDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DepartmentMkt.objects.all()
    serializer_class = DepartmentMktSerializer

def Show(request):
    try:
        # Get the department marketing info
        department = DepartmentMkt.objects.first()
        department_data = DepartmentMktSerializer(department).data if department else None

        # Get the latest comments
        customer_score = Comment.objects.aggregate(avg_score=Avg('score'))['avg_score']
        customer_score = customer_score if customer_score else 'NULL'
        comments = Comment.objects.order_by('-id').values("day", "name", "score", "content")[:5]

        data = {
            'department': department_data,
            'score': customer_score,
            'comments': list(comments)
        }
        return JsonResponse(data, status=200)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
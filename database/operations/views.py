from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .models import Operations
from .serializers import OperationsSerializer
from comment.models import Comment

class OperationsListView(generics.ListCreateAPIView):
    queryset = Operations.objects.all()
    serializer_class = OperationsSerializer

class OperationsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Operations.objects.all()
    serializer_class = OperationsSerializer

def Show(request):
    try:
        # Get the operations info
        operations = Operations.objects.first()
        operations_data = OperationsSerializer(operations).data if operations else None

        data = {
            'operations': operations_data
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def operations_dashboard(request):
    operations = Operations.objects.all()
    # Calculate summary metrics
    total_income = sum(op.income for op in operations)
    total_expenses = sum(op.expenses for op in operations)
    avg_score_product = sum(op.score_product for op in operations) / len(operations) if operations else 0
    avg_score_ad = sum(op.score_add for op in operations) / len(operations) if operations else 0
    
    context = {
        'operations': operations,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'profit': total_income - total_expenses,
        'avg_score_product': avg_score_product,
        'avg_score_ad': avg_score_ad,
    }
    return render(request, 'operations/dashboard.html', context)

def get_last_comment(request):
    try:
        last_comment = Comment.objects.order_by('-created_at').first()
        if last_comment:
            return JsonResponse({
                'comment': {
                    'id': last_comment.id,
                    'text': last_comment.text,
                    'created_at': last_comment.created_at.isoformat()
                }
            })
        return JsonResponse({'comment': None})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

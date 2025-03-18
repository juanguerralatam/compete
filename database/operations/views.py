from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from .models import Operations
from .serializers import OperationsSerializer

# List all operations entries
class OperationsListView(generics.ListCreateAPIView):
    queryset = Operations.objects.all()
    serializer_class = OperationsSerializer

# View details of a specific operations entry
class OperationsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Operations.objects.all()
    serializer_class = OperationsSerializer

# Function-based view for operations dashboard
def get_last_comment(request):
    # Get the most recent comment from the database
    latest_comment = Comment.objects.order_by('-created_at').first()
    
    if latest_comment:
        return JsonResponse({
            'id': latest_comment.id,
            'content': latest_comment.content,
            'created_at': latest_comment.created_at
        })
    return JsonResponse({'error': 'No comments found'}, status=404)


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

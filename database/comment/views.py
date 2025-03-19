from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Avg
from .models import Comment
from .serializers import CommentSerializer

class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

def Show(request):
    try:
        # Get the comments and score
        customer_score = Comment.objects.aggregate(avg_score=Avg('score'))['avg_score']
        customer_score = round(customer_score, 2) if customer_score else None
        comments = Comment.objects.order_by('-id').values("month", "name", "score", "content")[:5]

        data = {
            'score': customer_score,
            'comments': list(comments)
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_last_comment(request):
    try:
        # Get the most recent comment
        last_comment = Comment.objects.order_by('-id').first()
        comment_data = CommentSerializer(last_comment).data if last_comment else None

        if not comment_data:
            return JsonResponse({'error': 'No comments found'}, status=404)

        data = {
            'comment': comment_data
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Max

from .models import Comment
from .serializers import CommentSerializer

class CommentListView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
def get_last_comment(self):
    # Determine the maximum value of the 'month' field
    max_month = Comment.objects.aggregate(Max('month'))['month__max']
    # Filter based on this maximum value and get the 'name' and 'content' fields
    comments = Comment.objects.filter(month=max_month).values("name", "content")
    comments = list(comments)
    return JsonResponse(comments, status=200, safe=False)
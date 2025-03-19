from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Avg
from .models import BasicInfo
from ads.models import Ads
from products.models import Products
from comment.models import Comment
from .serializers import BasicInfoSerializer

class BasicInfoListView(generics.ListCreateAPIView):
    queryset = BasicInfo.objects.all()
    serializer_class = BasicInfoSerializer

class BasicInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BasicInfo.objects.all()
    serializer_class = BasicInfoSerializer

def Show(request):
    try:
        # Get the basic info
        basic_info = BasicInfo.objects.first()
        name = basic_info.name if basic_info else None

        # Get the ads
        ads = Ads.objects.first()
        ads_content = ads.content if ads else None

        # Get the products
        products = Products.objects.values("id", "name", "price", "description")

        # Get the comments and score
        customer_score = Comment.objects.aggregate(avg_score=Avg('score'))['avg_score']
        customer_score = round(customer_score, 2) if customer_score else None
        comments = Comment.objects.order_by('-id').values("day", "name", "score", "content")[:5]

        data = {
            'name': name,
            'score': customer_score,
            'ads': ads_content,
            'products': list(products),
            'comments': list(comments),
        }
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
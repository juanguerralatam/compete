from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from .models import BasicInfo
from ads.models import Ads
from products.models import Products
from .serializers import BasicInfoSerializer

class BasicInfoListView(generics.ListCreateAPIView):
    queryset = BasicInfo.objects.all()
    serializer_class = BasicInfoSerializer

class BasicInfoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BasicInfo.objects.all()
    serializer_class = BasicInfoSerializer

def Show(request):

    # print(BasicInfo.objects.count())
    try:
        # Get the basic info from the database (assuming there's only one record)
        basic_info = BasicInfo.objects.first()
        name = basic_info.name if basic_info else None

        try:
            ads = Ads.objects.first()
            ads = ads.content if ads else None
        except NameError:
            ads = None

        # Get the menu items and exclude the 'price_cost' field
        products = Products.objects.values("id", "name", "price", "description")
        # Get the comments from Comment
        customer_score = Comment.objects.aggregate(avg_score=Avg('score'))['avg_score']
        customer_score = customer_score if customer_score else 'NULL'
        comment = Comment.objects.order_by('-id').values("day", "name", "score", "content")[:5]

        data = {
            'name': name,
            'score': customer_score,
            'ads': ads,
            'products': list(products),
            'comment': list(comment),
        }
        return JsonResponse(data, status=200)
    
    except Exception as e:
        # Handle exceptions, e.g., database connection issues
        return JsonResponse({'error': str(e)}, status=500)
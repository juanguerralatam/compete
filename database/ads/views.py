from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from .models import Ads
from .serializers import AdsSerializer

class AdsListView(generics.ListCreateAPIView):
    queryset = Ads.objects.all()
    serializer_class = AdsSerializer

class AdsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ads.objects.all()
    serializer_class = AdsSerializer

def Show(request):
    try:
        # Get the ads info
        ads = Ads.objects.first()
        ads_data = AdsSerializer(ads).data if ads else None

        data = {
            'ads': ads_data
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Function-based view for ads dashboard
def ads_dashboard(request):
    ads = Ads.objects.all()
    # Calculate ad metrics
    total_ads = ads.count()
    active_ads = ads.filter(is_active=True).count()
    avg_cost = sum(ad.cost for ad in ads) / total_ads if total_ads > 0 else 0
    
    context = {
        'ads': ads,
        'total_ads': total_ads,
        'active_ads': active_ads,
        'avg_cost': avg_cost,
    }
    return render(request, 'ads/dashboard.html', context)

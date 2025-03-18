from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics
from .models import Ads
from .serializers import AdsSerializer

class AdsListView(generics.ListCreateAPIView):
    queryset = Ads.objects.all()
    serializer_class = AdsSerializer

class AdsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ads.objects.all()
    serializer_class = AdsSerializer

# Function-based view for ads dashboard
def ads_dashboard(request):
    ads = Ads.objects.all()
    total_ads = ads.count()
    
    context = {
        'ads': ads,
        'total_ads': total_ads,
    }
    return render(request, 'ads/dashboard.html', context)

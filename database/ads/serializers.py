from rest_framework import serializers
from .models import Ads

class AdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ads
        fields = ['id', 'content']
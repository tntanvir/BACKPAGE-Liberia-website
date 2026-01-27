from rest_framework import serializers
from .models import Ads, AdsPage

class AdsPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdsPage
        fields = '__all__'

class AdsSerializer(serializers.ModelSerializer):
    page = serializers.SlugRelatedField(slug_field='name', queryset=AdsPage.objects.all())

    class Meta:
        model = Ads
        fields = ['page', 'image', 'link', 'created_at', 'updated_at']

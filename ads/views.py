from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Ads, AdsPage
from .serializers import AdsSerializer, AdsPageSerializer

class AdsPageView(generics.ListCreateAPIView):
    queryset = AdsPage.objects.all()
    serializer_class = AdsPageSerializer


# Create your views here.

class AdsListView(APIView):
    def get(self, request):
        page_name = request.query_params.get('page')
        
        if page_name:
            ads = Ads.objects.filter(page__name__icontains=page_name)
        else:
            ads = Ads.objects.all()
            
        serializer = AdsSerializer(ads, many=True)
        data = serializer.data
        
        # Transform the list into the requested dictionary format
        formatted_response = {}
        for index, item in enumerate(data, start=1):
            formatted_response[str(index)] = item
            
        return Response(formatted_response, status=status.HTTP_200_OK)

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Ads
from .serializers import AdsSerializer

# Create your views here.

class AdsListView(APIView):
    def get(self, request):
        page_name = request.query_params.get('page')
        
        if page_name:
            ads = Ads.objects.filter(page=page_name)
        else:
            ads = Ads.objects.all()
            
        serializer = AdsSerializer(ads, many=True)
        data = serializer.data
        
        # Transform the list into the requested dictionary format
        formatted_response = {}
        for index, item in enumerate(data, start=1):
            formatted_response[str(index)] = item
            
        return Response(formatted_response, status=status.HTTP_200_OK)

import logging
import os

from celery.result import AsyncResult
from django.db.models import Count, F
from django.http import FileResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Video, Videoview, VideoCategory
from .serializers import (
    AnalyzeSerializer,
    DownloadSerializer,
    VideoSerializer,
    VideoviewSerializer,
    VideoCategorySerializer,
)
from .services import VideoDownloaderService
from .tasks import download_video_task
from .utils import FileCleanupWrapper

logger = logging.getLogger(__name__)

# Create your views here.

class VideoListCreateView(APIView):
    def get(self, request):
        queryset = Video.objects.all()
        
        # Search by title
        title_search = request.query_params.get('search')
        if title_search:
            queryset = queryset.filter(title__icontains=title_search)
        
        # Filter by category name
        category_filter = request.query_params.get('category')
        if category_filter:
            queryset = queryset.filter(category__name__iexact=category_filter)
        
        # Sort by newest/oldest
        sortby = request.query_params.get('sortby')
        if sortby == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sortby == 'oldest':
            queryset = queryset.order_by('created_at')
            
        serializer = VideoSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VideoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoDetailView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Video, pk=pk)

    def get(self, request, pk):
        video = self.get_object(pk)
        serializer = VideoSerializer(video)
        return Response(serializer.data)

    def put(self, request, pk):
        video = self.get_object(pk)
        serializer = VideoSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        video = self.get_object(pk)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnalyzeView(APIView):
   def post(self, request):
       serializer = AnalyzeSerializer(data=request.data)
       if serializer.is_valid():
           url = serializer.validated_data['url']
           service = VideoDownloaderService()
           try:
               data = service.analyze(url)
               return Response(data, status=status.HTTP_200_OK)
           except Exception as e:
               err_msg = str(e)
               if "429" in err_msg:
                   return Response({"error": "Too many requests to video provider"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
               if "403" in err_msg or "Private" in err_msg:
                    return Response({"error": "Content is private or rectricted"}, status=status.HTTP_403_FORBIDDEN)
              
               logger.error(f"Analysis Error: {e}")
               return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DownloadView(APIView):
   def post(self, request):
       """
       Initiates the download task and returns a Task ID.
       """
       serializer = DownloadSerializer(data=request.data)
       if serializer.is_valid():
           url = serializer.validated_data['url']
           format_id = serializer.validated_data['format_id']
          
           music_id = serializer.validated_data.get('music_id') or None
           user_id = request.user.id if request.user.is_authenticated else None
           
           # Dispatch Async Task
           task = download_video_task.delay(url, format_id, music_id=music_id, user_id=user_id)
          
           return Response({
               "task_id": task.id,
               "status": "processing",
               "message": "Download started successfully. Poll /api/v1/status/<task_id>/ for updates."
           }, status=status.HTTP_202_ACCEPTED)


       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskStatusView(APIView):
   def get(self, request, task_id):
       """
       Check the status of a download task.
       """
       result = AsyncResult(task_id)
      
       response_data = {
           "task_id": task_id,
           "status": result.state,
       }


       if result.state == 'SUCCESS':
           # Construct the retrieve URL
           # In a real app, use reverse(). For now, simple string construction.
           # We assume the client knows where to go, or we provide the link.
           response_data['download_url'] = f"/api/video/retrieve/{task_id}/"
       elif result.state == 'FAILURE':
           response_data['error'] = str(result.result)


       return Response(response_data)


class FileRetrieveView(APIView):
   def get(self, request, task_id):
       """
       Retrieve the downloaded file (once task is SUCCESS).
       """
       result = AsyncResult(task_id)
      
       if result.state != 'SUCCESS':
           return Response({"error": "Task not ready or failed"}, status=status.HTTP_400_BAD_REQUEST)
      
       # Result is the dict we returned in tasks.py
       data = result.result
       file_path = data.get('file_path')
       temp_dir = data.get('temp_dir')
      
       if not file_path or not os.path.exists(file_path):
            return Response({"error": "File expired or not found"}, status=status.HTTP_404_NOT_FOUND)


       filename = os.path.basename(file_path)
      
       # Cleanup Wrapper will delete the file/folder after streaming
       try:
           file_handle = FileCleanupWrapper(file_path, temp_dir)
           response = FileResponse(file_handle, as_attachment=True, filename=filename)
           response['Content-Length'] = os.path.getsize(file_path)
          
           # Optional: We might want to forget the task result now to save Redis memory,
           # but default expiry is usually fine.
           # result.forget()
          
           return response
       except Exception as e:
           logger.error(f"Retrieve Error: {e}")
           return Response({"error": "Error retrieving file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MusicVideoListView(APIView):
    def get(self, request):
        videos = Video.objects.filter(tag='music_video')
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

class MovieListView(APIView):
    def get(self, request):
        videos = Video.objects.filter(tag='movie')
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)

class TrendingVideoListView(APIView):
    def get(self, request):
        # Annotate with total view counts and order by it
        videos = Video.objects.annotate(
            total_views=Count('videoview')
        ).order_by('-total_views')
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data)



class VideoViewCreateView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Expects {"video": <id>}
        serializer = VideoviewSerializer(data=request.data)
        
        video_id = request.data.get('video')
        if not video_id:
             return Response({"error": "Video ID required"}, status=status.HTTP_400_BAD_REQUEST)

        video = get_object_or_404(Video, pk=video_id)
        
        # Check if a Videoview exists for this video
        # We assume one Videoview object per Video to aggregate counts
        view_obj, created = Videoview.objects.get_or_create(video=video)
        view_obj.view_count += 1
        view_obj.save()
        
        return Response({"message": "View recorded", "total_views": view_obj.view_count}, status=status.HTTP_201_CREATED)

class VideoCategoryListView(APIView):
    def get(self, request):
        categories = VideoCategory.objects.all()
        serializer = VideoCategorySerializer(categories, many=True)
        return Response(serializer.data)


class NewReleaseListView(APIView):
    def get(self, request):
       videos = Video.objects.all().order_by('-created_at')[:5]
       serializer = VideoSerializer(videos, many=True)
       return Response(serializer.data)
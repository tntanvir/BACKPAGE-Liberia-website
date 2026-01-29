from celery import shared_task
from .services import VideoDownloaderService
from artist.models import Music, Download
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True)
def download_video_task(self, url, format_id, music_id=None, user_id=None):
   """
   Async task to download video.
   Returns dictionary with file_path and temp_dir to be used by the retrieve view.
   """
   try:
       service = VideoDownloaderService()
       file_path, temp_dir = service.download(url, format_id)
       
       # Track Music Download
       if music_id:
           try:
               music = Music.objects.get(id=music_id)
               music.total_downloads += 1
               music.save()
               
               if user_id:
                   try:
                       user = User.objects.get(id=user_id) or None 
                       Download.objects.create(user=user, music=music)
                   except User.DoesNotExist:
                       logger.warning(f"User {user_id} not found for download tracking")
           except Music.DoesNotExist:
               logger.warning(f"Music {music_id} not found for download tracking")
           except Exception as e:
               logger.error(f"Error tracking download: {e}")
      
       # We return the paths as strings.
       # Note: In a diverse worker env, workers and web must share the filesystem.
       # Since this is a simple setup on one machine (or mounted volume), this is fine.
       return {
           'file_path': str(file_path),
           'temp_dir': str(temp_dir)
       }
   except Exception as e:
       logger.error(f"Task failed: {e}")
       # Re-raise so Celery marks it as FAILED
       raise e

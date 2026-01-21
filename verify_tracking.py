import os
import django
from unittest.mock import MagicMock, patch

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackPage.settings')
django.setup()

from video.tasks import download_video_task
from artist.models import Music, Artist, Download
from django.contrib.auth import get_user_model

def verify_tracking():
    User = get_user_model()
    
    # Create dummy data
    user, _ = User.objects.get_or_create(email='test@example.com', defaults={'name': 'Test Downloader'})
    artist, _ = Artist.objects.get_or_create(name='Test Artist', artist_type='local', location='Test City')
    music, _ = Music.objects.get_or_create(
        title='Test Song', 
        artist=artist, 
        defaults={'image': 'test.jpg', 'audio': 'test.mp3'}
    )
    
    initial_downloads = music.total_downloads
    print(f"Initial Downloads: {initial_downloads}")
    
    # Mock the downloader service to avoid actual networking
    with patch('video.tasks.VideoDownloaderService') as MockService:
        mock_instance = MockService.return_value
        # Mock download to return dummy paths
        mock_instance.download.return_value = ('/tmp/dummy_file.mp4', '/tmp/dummy_dir')
        
        # Call the task properly
        print("Calling download task...")
        download_video_task(
            url='http://example.com/video', 
            format_id='best', 
            music_id=music.id, 
            user_id=user.id
        )
        
    # Verify updates
    music.refresh_from_db()
    print(f"Final Downloads: {music.total_downloads}")
    
    if music.total_downloads == initial_downloads + 1:
        print("SUCCESS: Music download count incremented.")
    else:
        print("FAILURE: Music download count did NOT increment.")
        
    # Verify Download record
    download_exists = Download.objects.filter(user=user, music=music).exists()
    if download_exists:
        print("SUCCESS: Download record created.")
    else:
        print("FAILURE: Download record NOT created.")

if __name__ == "__main__":
    verify_tracking()

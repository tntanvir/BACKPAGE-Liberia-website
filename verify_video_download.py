import os
import django
from django.conf import settings
from unittest.mock import MagicMock, patch

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackPage.settings')
django.setup()

from video.services import VideoDownloaderService

def verify_generic_download():
    print("Verifying Generic File Download (S3 fallback)...")
    
    service = VideoDownloaderService()
    url = "https://ropeace.s3.amazonaws.com/music/test_file.mp3?some=param"
    
    # Mock yt_dlp.YoutubeDL to fail on extract_info
    # We patch the class constructor
    with patch('yt_dlp.YoutubeDL') as MockYTDL:
        # Configure the mock instance
        mock_instance = MockYTDL.return_value
        mock_instance.__enter__.return_value = mock_instance
        mock_instance.extract_info.side_effect = Exception("yt-dlp failed as expected")
        
        # Mock requests.get to succeed
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {'Content-Disposition': 'attachment; filename="downloaded_test.mp3"'}
            mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
            
            mock_get.return_value.__enter__.return_value = mock_response
            
            print("Attempting download...")
            try:
                path, temp_dir = service.download(url, 'best')
                print(f"Download returned path: {path}")
                
                if "downloaded_test.mp3" in path:
                    print("SUCCESS: Service fell back to requests and used Content-Disposition filename.")
                    return True
                else:
                    print(f"FAILURE: Filename unexpected: {path}")
                    return False
                    
            except Exception as e:
                print(f"FAILURE: Service raised exception: {e}")
                import traceback
                traceback.print_exc()
                return False

if __name__ == "__main__":
    success = verify_generic_download()
    if success:
        print("\nVerification Passed!")
    else:
        print("\nVerification Failed!")

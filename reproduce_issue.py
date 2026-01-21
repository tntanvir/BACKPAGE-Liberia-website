from video.services import VideoDownloaderService
import logging
import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackPage.settings')
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_direct_download():
    service = VideoDownloaderService()
    
    # A standard MP3 file (direct link)
    # This acts like an S3 link
    url = "https://www.w3schools.com/html/horse.mp3"
    
    print(f"Testing Analysis for: {url}")
    try:
        result = service.analyze(url)
        print("Analysis Result:")
        print(f"Title: {result['title']}")
        print(f"Source: {result['source']}")
        print(f"Formats: {len(result['formats'])}")
        
        for fmt in result['formats']:
            print(f" - ID: {fmt['format_id']}, Ext: {fmt['ext']}, Note: {fmt['note']}")
            
        if result['source'] == 'generic' and len(result['formats']) >= 1:
            print("\nSUCCESS: Generic file analysis worked!")
        else:
            print("\nFAILURE: Did not detect as generic or no formats found.")
            
    except Exception as e:
        print(f"Analysis Failed: {e}")

if __name__ == "__main__":
    test_direct_download()

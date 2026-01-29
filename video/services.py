import os
import uuid
import shutil
import logging
import yt_dlp
import requests
from urllib.parse import urlparse, unquote
from django.conf import settings
from pathlib import Path


logger = logging.getLogger(__name__)


class VideoDownloaderService:
    def __init__(self):
        self.base_opts = {
            'quiet': True,
            'noplaylist': True,
            'force_ipv4': True,
            'cookiefile': '/app/cookies.txt',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                }
            }
        }


    def _get_filesize_str(self, filesize):
        if not filesize:
            return "Unknown"
        return f"{filesize / (1024 * 1024):.2f} MB"


    def analyze(self, url):
        """Extract metadata and available formats for the given URL."""
        opts = self.base_opts.copy()
       
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)


            formats = []
            raw_formats = info.get('formats', [])


            # Identify best audio for merging if needed
            best_audio_id = None
            audio_formats = [f for f in raw_formats if f.get('vcodec') == 'none' and f.get('acodec') != 'none']
            if audio_formats:
                best_audio_id = audio_formats[-1]['format_id']


            for f in raw_formats:
                vcodec = f.get('vcodec')
                acodec = f.get('acodec')
                height = f.get('height')
                filesize = f.get('filesize') or f.get('filesize_approx')


                # Skip audio-only
                if vcodec == 'none':
                    continue
               
                # Determine if merge is needed (Video-only 1080p+ usually)
                needs_merge = False
                if acodec == 'none' and vcodec != 'none':
                    needs_merge = True


                format_id = f['format_id']
                if needs_merge and best_audio_id:
                    format_id = f"{format_id}+{best_audio_id}"
               
                resolution = f"{height}p" if height else "Unknown"
                if not height:
                    resolution = "Auto/Best"


                # TikTok HD Check
                note = f.get('format_note') or ''
                if info.get('extractor_key') == 'TikTok' and height and height >= 1080:
                     note = "HD"
               
                if needs_merge:
                     note = f"{note} (Merged)" if note else "(Merged)"


                formats.append({
                    "format_id": format_id,
                    "resolution": resolution,
                    "ext": f.get('ext', 'mp4'),
                    "filesize": self._get_filesize_str(filesize),
                    "note": note.strip()
                })


            formats.insert(0, {
                "format_id": "best",
                "resolution": "Best Available",
                "ext": "mp4",
                "filesize": "Unknown",
                "note": "Let server decide"
            })
           
            # Remove duplicates
            unique_formats = []
            seen_ids = set()
            for fmt in formats:
                if fmt['format_id'] not in seen_ids:
                    unique_formats.append(fmt)
                    seen_ids.add(fmt['format_id'])


            unique_formats.reverse()


            return {
                "status": "success",
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "source": info.get('extractor_key'),
                "duration": info.get('duration_string'),
                "formats": unique_formats
            }


        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise Exception(f"Analysis failed: {str(e)}")


    def download(self, url, format_id):
        """Download the video and return the file path and temp dir."""
        request_id = str(uuid.uuid4())
        temp_dir = settings.MEDIA_ROOT / 'temp' / request_id
        temp_dir.mkdir(parents=True, exist_ok=True)


        opts = self.base_opts.copy()
       
        # Format selection logic
        if format_id == 'best':
            if "tiktok.com" in url:
                opts['format'] = "best[height>=1280]/best[height>=1080]/best"
            else:
                opts['format'] = 'bestvideo+bestaudio/best'
        else:
            opts['format'] = format_id


        # Merge output format to MP4 if needed
        if '+' in format_id or opts.get('format', '') == 'bestvideo+bestaudio/best':
             opts['merge_output_format'] = 'mp4'


        # Limit filename length to 50 characters to prevent filesystem errors (especially with Unicode)
        opts['outtmpl'] = str(temp_dir / '%(title).50s.%(ext)s')
        opts['trim_file_name'] = 50
       
        save_path = None


        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
               
                # Check extension drift after merge
                if opts.get('merge_output_format') == 'mp4':
                     path_obj = Path(filename)
                     if path_obj.suffix != '.mp4':
                         filename = str(path_obj.with_suffix('.mp4'))
               
                save_path = filename


            if save_path and os.path.exists(save_path):
                return save_path, temp_dir
            else:
                 # Fallback search
                 files = list(temp_dir.glob('*'))
                 if files:
                     return str(files[0]), temp_dir
                 raise Exception("File not found after download.")


        except Exception as e:
            logger.warning(f"yt-dlp download failed ({e}). Attempting fallback download...")
            
            # Fallback: Direct Download
            try:
                # 1. Parse filename from URL
                parsed_url = urlparse(url)
                path = unquote(parsed_url.path)
                filename = os.path.basename(path)
                
                # Default if empty or invalid
                if not filename or '.' not in filename:
                    filename = f"download_{request_id}.mp4" 
                
                # If we're guessing based on context, we default to whatever we found or generic
                save_path_obj = temp_dir / filename
                
                # 2. Stream download using requests
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    
                    # Try to get filename from Content-Disposition if available
                    if 'Content-Disposition' in r.headers:
                        import re
                        # Simple regex to extract filename="foo.bar"
                        fname = re.findall(r'filename="?([^"]+)"?', r.headers['Content-Disposition'])
                        if fname:
                            filename = fname[0]
                            save_path_obj = temp_dir / filename

                    with open(save_path_obj, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192): 
                            if chunk:
                                f.write(chunk)
                
                if save_path_obj.exists():
                     return str(save_path_obj), temp_dir
                
            except Exception as fallback_e:
                logger.error(f"Fallback download also failed: {fallback_e}")
                
            
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise Exception(f"Download failed: {str(e)}. Fallback failed: {str(fallback_e)}")

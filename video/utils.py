import os
import shutil
import logging


logger = logging.getLogger(__name__)


class FileCleanupWrapper:
   """
   Wraps a file object to delete the file and its temporary directory
   when the file is closed.
   """
   def __init__(self, file_path, temp_dir):
       self.file_path = file_path
       self.temp_dir = temp_dir
       self._file = open(file_path, 'rb')


   def read(self, size=-1):
       return self._file.read(size)


   def __iter__(self):
       return self._file


   def close(self):
       self._file.close()
       try:
           if os.path.exists(self.temp_dir):
               shutil.rmtree(self.temp_dir)
               logger.info(f"Cleaned up temp dir: {self.temp_dir}")
       except Exception as e:
           logger.error(f"Error cleaning up {self.temp_dir}: {e}")


   def seek(self, offset, whence=0):
       return self._file.seek(offset, whence)
      
   def tell(self):
       return self._file.tell()

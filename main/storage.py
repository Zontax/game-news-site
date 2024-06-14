from django.core.files.storage import FileSystemStorage

from app.settings.base import MEDIA_ROOT, MEDIA_URL
from urllib.parse import urljoin
from datetime import datetime
import os


class CkeditorStorage(FileSystemStorage):
    """
    Custom storage for django_ckeditor_5 images.
    """

    def get_folder_name(self):
        return datetime.now().strftime('%Y/%m/%d')

    def get_valid_name(self, name):
        return name

    def _save(self, name, content):
        folder_name = self.get_folder_name()
        name = os.path.join(folder_name, self.get_valid_name(name))
        return super()._save(name, content)

    location = MEDIA_ROOT / 'images/posts/'
    base_url = urljoin(MEDIA_URL, 'images/posts/')

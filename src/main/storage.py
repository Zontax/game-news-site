import os
from datetime import datetime
from urllib.parse import urljoin
from django.core.files.storage import FileSystemStorage
from core.settings.base import MEDIA_ROOT, MEDIA_URL


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

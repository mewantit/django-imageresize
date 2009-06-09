from django.conf import settings
import os

settings.configure()

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))

RESIZE_MAX_HEIGHT=2048
RESIZE_MAX_WIDTH=2048

MEDIA_ROOT=""
MEDIA_CACHE_ROOT=""

TEST_MEDIA_ROOT=os.path.join(PROJECT_PATH, 'test_media')

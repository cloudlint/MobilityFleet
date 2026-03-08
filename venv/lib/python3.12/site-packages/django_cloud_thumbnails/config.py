from appconf import AppConf

from django.conf import settings


class DjangoCloudThumbnailsAppConf(AppConf):
    THUMB_SIZE = (300, 300)
    SIZE_WARNING = False
    BACKEND = 'django_cloud_thumbnails.backends.cloud_thumbnails.CloudThumbnailsBackend'
    BACKEND_PARAMS = {}
    JQUERY_URL = settings.STATIC_URL + 'admin/js/vendor/jquery/jquery.min.js'

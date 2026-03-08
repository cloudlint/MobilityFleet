from .base import ImageBackend

from ..utils import pil_image, storage_url


class CloudThumbnailsBackend(ImageBackend):
    exceptions_to_catch = (IOError,)

    def get_thumbnail_url(self, image, thumbnail_options):
        width = thumbnail_options['size'][0]
        height = thumbnail_options['size'][1]

        return storage_url(image, width, height)

    def get_size(self, image):
        return pil_image(image).size

from io import BytesIO

from PIL import Image
from PIL.ImageFile import ImageFile
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.db.models import ImageField, CharField
from django.db.models.fields.files import ImageFieldFile
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _
from django_cloud_storage.storage import CloudStorage

from .config import settings


def max_cropping(width, height, image_width, image_height, free_crop=False):
    if free_crop:
        return [0, 0, image_width, image_height]

    ratio = width / float(height)
    if image_width < image_height * ratio:
        offset = int(round((image_height - (image_width / ratio)) / 2))
        return [0, offset, image_width, image_height - offset]

    offset = int(round((image_width - (image_height * ratio)) / 2))
    return [offset, 0, image_width - offset, image_height]


def get_backend():
    try:
        cls = import_string(settings.DJANGO_CLOUD_THUMBNAILS_BACKEND)
    except ImportError as e:
        raise ImproperlyConfigured(
            _("Can't retrieve the image backend '{}'. Message: '{}'.").format(
                settings.DJANGO_CLOUD_THUMBNAILS_BACKEND, e
            )
        )

    return cls(**settings.DJANGO_CLOUD_THUMBNAILS_BACKEND_PARAMS)


storage = CloudStorage()


def storage_url(image: ImageFieldFile, width: int = None, height: int = None) -> str:
    return storage.url(image.name, width, height)


def pil_image(image: ImageFieldFile):
    if not image:
        return

    source = BytesIO(image.read())

    img = Image.open(source)

    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        img.load()
    finally:
        ImageFile.LOAD_TRUNCATED_IMAGES = False

    return img


def crop(crop_field: ImageField, ratio_field: CharField) -> ContentFile:
    file = storage.open(crop_field.name)

    image = pil_image(file)
    image_format = image.format

    if ratio_field:
        box = [int(x) for x in str(ratio_field).split(',')]
        image = image.crop((box[0], box[1], box[2], box[3]))

    image_bytes = BytesIO()

    if image_format == 'JPG':
        image.save(image_bytes, format=image_format, quality=80)
    elif image_format == 'PNG':
        image.save(image_bytes, format=image_format, optimize=True, compress_level=9)
    elif image_format == 'WEBP':
        image.save(image_bytes, format=image_format, quality=80, method=6)
    else:
        image.save(image_bytes, format=image_format)

    return ContentFile(image_bytes.getvalue())

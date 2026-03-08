from django import forms
from django.db import models
from django.db.models import signals

from .config import settings
from .utils import get_backend, max_cropping
from .widgets import ImageCropWidget


class ImageCropField(models.ImageField):
    def formfield(self, **kwargs):
        defaults = {'widget': ImageCropWidget}
        defaults.update(kwargs)
        return super().formfield(**defaults)


def initial_cropping(sender, instance, *args, **kwargs):
    for ratio_field_name in getattr(instance, 'ratio_fields', []):
        if getattr(instance, ratio_field_name):
            continue

        ratio_field = instance._meta.get_field(ratio_field_name)
        image = getattr(instance, ratio_field.image_field)
        if ratio_field.image_fk_field and image:
            image = getattr(image, ratio_field.image_fk_field)
        if not image:
            continue

        try:
            width, height = (image.width, image.height)
        except AttributeError:
            width, height = get_backend().get_size(image)

        try:
            box = max_cropping(
                ratio_field.width,
                ratio_field.height,
                width,
                height,
                free_crop=ratio_field.free_crop,
            )
            box = ','.join(map(lambda i: str(i), box))
        except IOError:
            box = ''
        setattr(instance, ratio_field_name, box)


class ImageRatioField(models.CharField):
    def __init__(
            self,
            image_field,
            size='0x0',
            free_crop=False,
            adapt_rotation=False,
            allow_full_size=False,
            verbose_name=None,
            help_text=None,
            hide_image_field=False,
            size_warning=settings.DJANGO_CLOUD_THUMBNAILS_SIZE_WARNING,
    ):
        if '__' in image_field:
            self.image_field, self.image_fk_field = image_field.split('__')
        else:
            self.image_field, self.image_fk_field = image_field, None
        self.width, self.height = list(map(int, size.split('x')))
        self.free_crop = free_crop
        self.adapt_rotation = adapt_rotation
        self.allow_full_size = allow_full_size
        self.size_warning = size_warning
        self.hide_image_field = hide_image_field
        self.box_max_width = settings.DJANGO_CLOUD_THUMBNAILS_THUMB_SIZE[0]
        self.box_max_height = settings.DJANGO_CLOUD_THUMBNAILS_THUMB_SIZE[1]
        field_kwargs = {
            'max_length': 255,
            'default': '',
            'blank': True,
            'verbose_name': verbose_name,
            'help_text': help_text,
        }
        super().__init__(**field_kwargs)

    def deconstruct(self):
        if self.image_fk_field:
            image_field = '%s__%s' % (self.image_field, self.image_fk_field)
        else:
            image_field = self.image_field

        args = (image_field, '%dx%d' % (self.width, self.height))
        kwargs = {
            'free_crop': self.free_crop,
            'adapt_rotation': self.adapt_rotation,
            'allow_full_size': self.allow_full_size,
            'verbose_name': self.verbose_name,
            'help_text': self.help_text,
            'hide_image_field': self.hide_image_field,
            'size_warning': self.size_warning,
        }
        return self.name, 'django_cloud_thumbnails.fields.ImageRatioField', args, kwargs

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        if not cls._meta.abstract:
            if not hasattr(cls, 'crop_fields'):
                cls.add_to_class('crop_fields', {})
            cls.crop_fields[self.image_field] = {
                'fk_field': self.image_fk_field,
                'hidden': self.hide_image_field,
            }

            if not hasattr(cls, 'ratio_fields'):
                cls.add_to_class('ratio_fields', [])
            cls.ratio_fields.append(name)

            signals.pre_save.connect(initial_cropping, sender=cls)

    def formfield(self, **kwargs):
        ratio = self.width / float(self.height) if not self.free_crop else 0

        kwargs['widget'] = forms.TextInput(
            attrs={
                'data-min-width': self.width,
                'data-min-height': self.height,
                'data-box-max-width': self.box_max_width,
                'data-box-max-height': self.box_max_height,
                'data-ratio': str(ratio),
                'data-image-field': self.image_field,
                'data-my-name': self.name,
                'data-jquery-url': settings.DJANGO_CLOUD_THUMBNAILS_JQUERY_URL,
                'data-adapt-rotation': str(self.adapt_rotation).lower(),
                'data-allow-full-size': str(self.allow_full_size).lower(),
                'data-size-warning': str(self.size_warning).lower(),
                'class': 'image-ratio',
            }
        )
        return super().formfield(**kwargs)

from django import template

from ..utils import get_backend

register = template.Library()
VALID_OPTIONS = ('width', 'height')


@register.simple_tag(takes_context=True)
def cropped_thumbnail(context, instance, crop_field_name, **kwargs):
    """
    Syntax:
    {% cropped_thumbnail instance "crop_field_name" [width=100|height=200] %}
    """

    crop_field = getattr(instance, crop_field_name)

    width = kwargs.get('width')
    height = kwargs.get('height')

    thumbnail_options = {
        'size': (width, height),
        'crop': True,
        'detail': kwargs.pop('detail', True),
        'upscale': kwargs.pop('upscale', False),
    }

    for k in VALID_OPTIONS:
        kwargs.pop(k, None)

    thumbnail_options.update(kwargs)

    backend = get_backend()
    try:
        url = backend.get_thumbnail_url(crop_field, thumbnail_options)
    except backend.exceptions_to_catch:
        url = ''
    return url

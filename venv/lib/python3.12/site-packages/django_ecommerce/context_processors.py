from django_ecommerce.models import Setting
from django_ecommerce.utils import get_cart


def ecommerce_settings(request):
    return {
        'ecommerce_settings': Setting.get_solo()
    }


def ecommerce_cart(request):
    return {
        'ecommerce_cart': get_cart(request)
    }

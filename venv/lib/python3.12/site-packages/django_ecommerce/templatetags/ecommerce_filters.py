from django import template

from django_ecommerce.utils import variant_availability, chunks, similar_products

register = template.Library()

register.filter(chunks)
register.filter(similar_products)
register.filter(variant_availability)

from typing import Callable

from django.conf import settings
from djmoney.money import Money

from django_ecommerce.models import ProductVariant, Setting, Order, OrderItem, City, Product, Category, Country


def chunks(queryset, chunk_size):
    chunk_size = int(chunk_size)

    return [queryset[i:i + chunk_size] for i in range(0, len(queryset), chunk_size)]


def similar_products(product, limit=4):
    category = product.category
    similar_items = Product.objects.filter(category=category).exclude(id=product.id)

    return similar_items.order_by('?')[:limit]


def variant_availability(variant: ProductVariant, request) -> int:
    cart_quantity = 0

    if str(variant.pk) in request.session.get('cart', {}):
        cart_quantity = request.session['cart'][str(variant.pk)]

    return variant.available_quantity - cart_quantity


def money(amount: float, currency: str = None) -> Money:
    if currency:
        return Money(amount, currency)

    if hasattr(settings, 'ECOMMERCE_DEFAULT_CURRENCY'):
        return Money(amount, getattr(settings, 'ECOMMERCE_DEFAULT_CURRENCY'))

    return Money(amount, 'EUR')


def get_shipping_data(amount: Money) -> dict:
    site_settings = Setting.get_solo()

    shipping = {
        'shipping_enabled': site_settings.shipping_enabled,
        'free_shipping_enabled': site_settings.free_shipping_enabled,
        'shipping_amount': site_settings.shipping_amount
    }

    if site_settings.shipping_enabled:
        if site_settings.free_shipping_enabled:
            shipping['free_shipping_remaining'] = site_settings.free_shipping_min_amount - amount
            shipping['is_free_shipping'] = (shipping['free_shipping_remaining']
                                            <= Money(0, site_settings.free_shipping_min_amount_currency))

            if shipping['is_free_shipping']:
                shipping['shipping_amount'] = money(0)

    return shipping


def get_cart(request):
    cart_total = money(0)
    cart_quantity = 0

    items = []
    remove = []

    for variant_id, quantity in request.session.get('cart', {}).items():
        try:
            if quantity <= 0:
                remove.append(variant_id)
                continue

            variant = ProductVariant.objects.get(pk=variant_id)

            if variant.available_quantity <= 0:
                remove.append(variant_id)
                continue

            if quantity > variant.available_quantity:
                quantity = variant.available_quantity

            total = variant.product.actual_price * quantity
            cart_total += total
            cart_quantity += quantity

            items.append({
                'variant': variant,
                'quantity': quantity,
                'total': total
            })
        except ProductVariant.DoesNotExist:
            continue

    if remove:
        for variant_id in remove:
            del request.session['cart'][variant_id]
            continue

        request.session.modified = True

    shipping = get_shipping_data(cart_total)

    if shipping['shipping_enabled'] and shipping['shipping_amount']:
        cart_total += shipping['shipping_amount']

    return {
        'items': items,
        'total': cart_total,
        'quantity': cart_quantity,
        'shipping': shipping,
    }


def remove_from_cart(request, variant_id: int) -> dict:
    if 'cart' in request.session and str(variant_id) in request.session['cart']:
        del request.session['cart'][str(variant_id)]
        request.session.modified = True

    return {}


def add_to_cart(request, variant_id: int, quantity: int = 1) -> dict:
    if variant_id and quantity:
        variant_id = int(variant_id or 0)
        quantity = int(quantity or 0)
        session_key = str(variant_id)

        try:
            variant = ProductVariant.objects.get(pk=variant_id)
        except ProductVariant.DoesNotExist:
            return {'error': f'ProductVariantDoesNotExist'}

        if 'cart' not in request.session:
            request.session['cart'] = {}

        if session_key in request.session['cart']:
            total_quantity = quantity + request.session['cart'][session_key]

            if variant.available_quantity < total_quantity:
                return {'error': f'StockError'}

            remaining = (variant.available_quantity - total_quantity) > 0

            if total_quantity <= 0:
                del request.session['cart'][session_key]
                request.session.modified = True
                return {'remaining': remaining}

            request.session['cart'][session_key] += quantity
            request.session.modified = True

            return {'remaining': remaining}

        if variant.available_quantity < quantity:
            return {'error': f'StockError'}

        remaining = (variant.available_quantity - quantity) > 0

        request.session['cart'][session_key] = quantity
        request.session.modified = True

        return {'remaining': remaining}

    return {'error': 'InvalidRequestOrParameters'}


def create_order(request, email: str = None, full_name: str = None, address: str = None, phone: str = None,
                 city: str = None, country: str = None, zip_code: str = None, remark: str = None,
                 func: Callable = None):
    cart = get_cart(request)

    if not cart['items']:
        return {'error': 'EmptyCart'}

    order = Order.objects.create(
        email=email,
        full_name=full_name,
        address=address,
        phone=phone,
        city=city,
        country=country,
        zip_code=zip_code,
        remark=remark,
        shipping_amount=cart['shipping']['shipping_amount'],
    )

    for item in cart['items']:
        OrderItem.objects.create(
            order=order,
            product_variant=item['variant'],
            price=item['variant'].product.price,
            discount_percentage=item['variant'].product.discount,
            quantity=item['quantity']
        )

    if func:
        func(request, order)

    del request.session['cart']

    return {'order': order}


def get_cities() -> set:
    return {city.name for city in City.objects.all()}


def get_countries() -> set:
    return {country.name for country in Country.objects.all()}


def find_product_by_slug(slug: str) -> Product | None:
    try:
        return Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return None


def find_category_by_slug(slug: str) -> Category | None:
    try:
        return Category.objects.get(slug=slug)
    except Category.DoesNotExist:
        return None


def find_order_by_code(code: str) -> Order | None:
    try:
        return Order.objects.get(code=code)
    except Order.DoesNotExist:
        return None

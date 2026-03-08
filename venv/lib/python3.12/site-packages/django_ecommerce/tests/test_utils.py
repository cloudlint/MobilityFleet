from unittest.mock import MagicMock

from django.test import TestCase
from django.test.utils import override_settings
from djmoney.money import Money

from django_ecommerce.models import Category, Product, Color, Gender, ProductVariant, StockImport, Warehouse, Stock, \
    Country, City, Order, Setting
from django_ecommerce.utils import chunks, money, similar_products, variant_availability, add_to_cart, create_order, \
    find_order_by_code, find_category_by_slug, find_product_by_slug, get_countries, get_cities, remove_from_cart, \
    get_cart, get_shipping_data


class UtilsTestCase(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Test')
        color = Color.objects.create(name='Blue')
        gender = Gender.objects.create(name='Unisex')
        Warehouse.objects.create(name='Warehouse1')

        p = Product.objects.create(name='Product1', category=category, color=color, gender=gender, price=money(10))
        ProductVariant.objects.create(product=p, name='Small', sku='PRODUCT1-SMALL')
        ProductVariant.objects.create(product=p, name='Medium', sku='PRODUCT1-MEDIUM')

        Product.objects.create(name='Product2', category=category, color=color, gender=gender, price=money(15))
        Product.objects.create(name='Product3', category=category, color=color, gender=gender, price=money(20))

    def test_chunks(self):
        queryset = [1, 2, 3, 4, 5, 6, 7, 8]
        chunk_size = 3
        result = chunks(queryset, chunk_size)

        self.assertEqual(result, [[1, 2, 3], [4, 5, 6], [7, 8]])

    def test_similar_products(self):
        similar = similar_products(Product.objects.first())
        self.assertTrue(similar)

    def test_variant_availability(self):
        product = Product.objects.first()
        request = self.client.get('/').wsgi_request

        # No stock
        self.assertEqual(variant_availability(product.variants.first(), request), 0)

        # Add to stock
        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)
        self.assertEqual(variant_availability(product.variants.first(), request), 5)

        # Add item to cart
        add_to_cart(request, product.variants.first().pk, 1)
        self.assertEqual(variant_availability(product.variants.first(), request), 4)

        # Create order and reserve items
        order = create_order(request)['order']
        for item in order.items.all():
            item.reserved = True
            item.save()

        self.assertEqual(variant_availability(product.variants.first(), request), 4)

    def test_money(self):
        # Currency argument is provided
        self.assertEqual(money(10, 'USD'), Money(10, 'USD'))

        # Currency argument is not provided, and we have default currency in settings
        with override_settings(ECOMMERCE_DEFAULT_CURRENCY='EUR'):
            self.assertEqual(money(10), Money(10, 'EUR'))

        # Default value for currency
        self.assertEqual(money(10), Money(10, 'EUR'))

    def test_get_shipping_data(self):
        product = Product.objects.first()

        # Shipping is not enabled
        shipping = get_shipping_data(product.price)
        self.assertFalse(shipping['shipping_enabled'])
        self.assertEqual(shipping['shipping_amount'], money(0))

        # Enable shipping
        ecommerce_settings = Setting.get_solo()
        ecommerce_settings.shipping_enabled = True
        ecommerce_settings.shipping_amount = money(3)
        ecommerce_settings.save()

        shipping = get_shipping_data(product.price)
        self.assertTrue(shipping['shipping_enabled'])
        self.assertEqual(shipping['shipping_amount'], money(3))

        # Enable free shipping
        ecommerce_settings.free_shipping_enabled = True
        ecommerce_settings.free_shipping_min_amount = 3 * product.price
        ecommerce_settings.save()

        shipping = get_shipping_data(2 * product.price)
        self.assertTrue(shipping['shipping_enabled'])
        self.assertTrue(shipping['free_shipping_enabled'])
        self.assertEqual(shipping['shipping_amount'], money(3))

        shipping = get_shipping_data(3 * product.price)
        self.assertTrue(shipping['shipping_enabled'])
        self.assertEqual(shipping['shipping_amount'], money(0))

    def test_get_cart(self):
        product = Product.objects.first()
        request = self.client.get('/').wsgi_request

        # Empty Cart
        cart = get_cart(request)
        self.assertEqual(cart['total'], money(0))
        self.assertEqual(cart['quantity'], 0)

        # Add item to cart and check again
        si = StockImport.objects.create()
        stock = Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(),
                                     quantity=5,
                                     content_object=si)

        self.assertEqual(add_to_cart(request, product.variants.first().pk, 2), {'remaining': True})

        cart = get_cart(request)
        self.assertEqual(cart['total'], 2 * product.price)
        self.assertEqual(cart['quantity'], 2)

        # Check if quantity is updated when stock is updated
        stock.quantity = 1
        stock.save()
        cart = get_cart(request)
        self.assertEqual(cart['total'], product.price)
        self.assertEqual(cart['quantity'], 1)

        # Check if item is removed from cart
        stock.delete()
        cart = get_cart(request)
        self.assertEqual(cart['total'], money(0))
        self.assertEqual(cart['quantity'], 0)

    def test_remove_from_cart(self):
        product = Product.objects.first()
        request = self.client.get('/').wsgi_request

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)

        self.assertEqual(add_to_cart(request, product.variants.first().pk, 3), {'remaining': True})
        remove_from_cart(request, product.variants.first().pk)
        self.assertNotIn(str(product.variants.first()), request.session.get('cart'))

    def test_add_to_cart(self):
        product = Product.objects.first()
        request = self.client.get('/').wsgi_request

        # Check invalid variant id
        self.assertEqual(add_to_cart(request, 12345), {'error': f'ProductVariantDoesNotExist'})

        # Check for stock data
        self.assertEqual(add_to_cart(request, product.variants.first().pk), {'error': f'StockError'})

        # Add stock and then add to cart
        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)

        self.assertEqual(add_to_cart(request, product.variants.first().pk, 4), {'remaining': True})
        self.assertEqual(add_to_cart(request, product.variants.first().pk, 1), {'remaining': False})
        self.assertEqual(add_to_cart(request, product.variants.first().pk, -1), {'remaining': True})

        # Check if it was removed from cart correctly
        add_to_cart(request, product.variants.first().pk, -4)
        self.assertNotIn(str(product.variants.first()), request.session.get('cart'))

    def test_create_order(self):
        product = Product.objects.first()
        request = self.client.get('/').wsgi_request

        # Create a mock function
        mock_func = MagicMock()

        # Order params
        params = {
            'email': 'test@example.com',
            'full_name': 'Hello World',
            'address': 'Test address',
            'phone': '1234567890',
            'city': 'Test',
            'country': 'Test',
            'zip_code': '123456',
            'remark': 'Test',
        }

        # Check when cart is empty
        self.assertEqual(create_order(request), {'error': 'EmptyCart'})

        # Add item to cart and create order
        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)

        add_to_cart(request, product.variants.first().pk, 2)
        result = create_order(request, func=mock_func, **params)

        # Assert that the order was created
        self.assertTrue('order' in result)
        order = result['order']
        self.assertIsInstance(order, Order)

        # Assert that the session cart is empty after order creation
        self.assertNotIn('cart', request)

        # Check if params were saved correctly
        for k, v in params.items():
            self.assertEqual(v, getattr(order, k))

        # Assert that the mock function was called with the expected arguments
        mock_func.assert_called_once_with(request, order)

        # Check if order item was saved correctly
        item = order.items.first()
        self.assertEqual(item.product_variant, product.variants.first())
        self.assertEqual(item.price, product.price)
        self.assertEqual(item.quantity, 2)

    def test_get_cities(self):
        c1 = City.objects.create(name='City1')
        c2 = City.objects.create(name='City1')

        self.assertEqual(get_cities(), {c1.name, c2.name})

    def test_get_countries(self):
        c1 = Country.objects.create(name='Country1')
        c2 = Country.objects.create(name='Country2')

        self.assertEqual(get_countries(), {c1.name, c2.name})

    def test_find_product_by_slug(self):
        p = Product.objects.first()

        self.assertEqual(find_product_by_slug(p.slug), p)

    def test_find_category_by_slug(self):
        c = Category.objects.create(name='MyCategory', slug='my-category')

        self.assertEqual(find_category_by_slug(c.slug), c)

    def test_find_order_by_code(self):
        product = Product.objects.first()

        request = self.client.get('/').wsgi_request

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)

        add_to_cart(request, product.variants.first().pk)

        order = create_order(request)['order']

        self.assertEqual(find_order_by_code(order.code), order)

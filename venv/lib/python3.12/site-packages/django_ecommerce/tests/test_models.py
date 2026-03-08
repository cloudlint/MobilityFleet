from datetime import datetime, timedelta

import pytz
from django.core.exceptions import ValidationError
from django.test import TestCase

from django_ecommerce.models import Category, Product, Color, Gender, ProductVariant, Warehouse, Discount, \
    DiscountCategory, \
    DiscountProduct, Stock, StockImport, Order, OrderItem, generate_order_code, Setting
from django_ecommerce.utils import money


class ModelsTestCase(TestCase):
    def setUp(self):
        product = Product.objects.create(
            name='Product1',
            category=Category.objects.create(name='Test'),
            color=Color.objects.create(name='Blue'),
            gender=Gender.objects.create(name='Unisex'),
            price=money(10)
        )

        ProductVariant.objects.create(product=product, name='Small', sku='PRODUCT1-SMALL')
        ProductVariant.objects.create(product=product, name='Medium', sku='PRODUCT1-MEDIUM')

        Warehouse.objects.create(name='Warehouse1')

    def test_category_discount_percentage(self):
        category = Category.objects.first()

        # No discount
        self.assertEqual(category.discount_percentage(), 0)

        # Create discount
        discount = Discount.objects.create(
            name='Discount1',
            start_date=datetime.now(tz=pytz.UTC),
            end_date=datetime.now(tz=pytz.UTC) + timedelta(days=7)
        )

        DiscountCategory.objects.create(discount=discount, category=category, percentage=10)

        self.assertEqual(category.discount_percentage(), 0)

        discount.active = True
        discount.save()

        self.assertEqual(category.discount_percentage(), 10)

    def test_product_discount_percentage(self):
        product = Product.objects.first()

        # No discount
        self.assertEqual(product.discount_percentage(), 0)

        # Create category discount
        discount = Discount.objects.create(
            name='Discount2',
            start_date=datetime.now(tz=pytz.UTC),
            end_date=datetime.now(tz=pytz.UTC) + timedelta(days=7),
            active=True
        )
        DiscountCategory.objects.create(discount=discount, category=product.category, percentage=20)
        self.assertEqual(product.discount_percentage(), 20)

        # Create product discount
        DiscountProduct.objects.create(discount=discount, product=product, percentage=30)
        self.assertEqual(product.discount_percentage(), 30)

    def test_product_get_actual_price(self):
        product = Product.objects.first()

        self.assertEqual(product.get_actual_price(), product.price)

        discount = Discount.objects.create(
            name='Discount3',
            start_date=datetime.now(tz=pytz.UTC),
            end_date=datetime.now(tz=pytz.UTC) + timedelta(days=7),
            active=True
        )

        DiscountProduct.objects.create(discount=discount, product=product, percentage=10)

        self.assertEqual(Product.objects.first().get_actual_price(), product.price * (100 - 10) / 100)

    def product_get_is_on_stock(self):
        product = Product.objects.first()

        self.assertFalse(product.get_is_on_stock())

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)

        self.assertTrue(product.get_is_on_stock())

    def test_product_variant_manager(self):
        product = Product.objects.first()

        # No stock
        variant = product.variants.first()
        self.assertEqual(variant.stock_quantity, 0)
        self.assertEqual(variant.reserved_quantity, 0)
        self.assertEqual(variant.available_quantity, 0)

        # Add stock
        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)
        variant = product.variants.first()
        self.assertEqual(variant.stock_quantity, 5)
        self.assertEqual(variant.reserved_quantity, 0)
        self.assertEqual(variant.available_quantity, 5)

        # Create order and reserve items
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product_variant=variant, quantity=3, price=product.price, reserved=True)

        variant = product.variants.first()
        self.assertEqual(variant.stock_quantity, 5)
        self.assertEqual(variant.reserved_quantity, 3)
        self.assertEqual(variant.available_quantity, 2)

    def test_product_variant_stock_data(self):
        product = Product.objects.first()
        warehouse = Warehouse.objects.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=warehouse, quantity=5,
                             content_object=si)

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=product.variants.first(), warehouse=warehouse, quantity=10,
                             content_object=si)

        self.assertEqual(product.variants.first().stock_data(), [(warehouse.name, 15)])

    def test_product_variant_reservations_data(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), quantity=5,
                             content_object=si)

        order = Order.objects.create()
        OrderItem.objects.create(order=order, product_variant=variant, quantity=3, price=product.price, reserved=True)

        self.assertEqual(variant.reservations_data(), [(order.code, 3)])

    def test_generate_order_code(self):
        code = generate_order_code()
        self.assertTrue(len(code) == 6)

    def test_order_total_amount(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), quantity=3,
                             content_object=si)

        order = Order.objects.create()
        OrderItem.objects.create(order=order, product_variant=variant, quantity=3, price=product.price, reserved=True)

        self.assertEqual(order.total_amount(), product.price * 3)

        # Enable shipping
        ecommerce_settings = Setting.get_solo()
        ecommerce_settings.shipping_enabled = True
        ecommerce_settings.shipping_amount = money(3)
        ecommerce_settings.save()

        order = Order.objects.create(shipping_amount=ecommerce_settings.shipping_amount)
        OrderItem.objects.create(order=order, product_variant=variant, quantity=3, price=product.price, reserved=True)

        self.assertEqual(order.total_amount(), product.price * 3 + ecommerce_settings.shipping_amount)

    def test_order_total_quantity(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), quantity=2,
                             content_object=si)

        order = Order.objects.create()
        OrderItem.objects.create(order=order, product_variant=variant, quantity=1, price=product.price, reserved=True)
        OrderItem.objects.create(order=order, product_variant=variant, quantity=1, price=product.price, reserved=True)

        self.assertEqual(order.total_quantity(), 2)

    def test_order_require_reserved_items(self):
        for status in Order.REQUIRE_RESERVED_ITEMS_STATUSES:
            order = Order.objects.create(status=status)
            self.assertTrue(order.require_reserved_items())

        order = Order.objects.create(status=Order.RETURN_TO_STOCK_STATUS)
        self.assertFalse(order.require_reserved_items())

    def test_order_can_modify_order_items(self):
        order = Order()
        self.assertTrue(order.can_modify_order_items())

        for status in Order.CAN_MODIFY_ORDER_ITEMS_STATUSES:
            order = Order.objects.create(status=status)
            self.assertTrue(order.can_modify_order_items())

        order = Order.objects.create(status=Order.RETURN_TO_STOCK_STATUS)
        self.assertFalse(order.can_modify_order_items())

    def test_order_status_changed(self):
        order = Order()
        order.status = Order.RETURN_TO_STOCK_STATUS
        self.assertTrue(order.status_changed())

    def test_order_check_status(self):
        for status in Order.ORDER_STATUSES:
            order = Order(status=status[0])
            allowed_statuses = Order.ALLOWED_STATUS_CHANGES[status[0]]

            for allowed in allowed_statuses:
                order.status = allowed
                try:
                    order.check_status()
                except ValidationError:
                    self.fail('ValidationError should not be raised')

    def test_order_remove_reservations(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), content_object=si,
                             quantity=5)

        order = Order.objects.create()
        OrderItem.objects.create(order=order, product_variant=variant, quantity=1, price=product.price, reserved=True)
        OrderItem.objects.create(order=order, product_variant=variant, quantity=1, price=product.price, reserved=True)

        order.remove_reservations()

        for item in order.items.all():
            self.assertFalse(item.reserved)

    def test_order_return_to_stock(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), content_object=si,
                             quantity=1)

        order = Order.objects.create()
        OrderItem.objects.create(
            order=order, product_variant=variant, quantity=1, price=product.price, reserved=True,
            warehouse=Warehouse.objects.first()
        )

        order.remove_from_stock()
        self.assertEqual(product.variants.first().stock_quantity, 0)

        order.return_to_stock()
        self.assertEqual(product.variants.first().stock_quantity, 1)

    def test_order_remove_from_stock(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), content_object=si,
                             quantity=2)

        order = Order.objects.create()
        OrderItem.objects.create(
            order=order, product_variant=variant, quantity=2, price=product.price, reserved=True,
            warehouse=Warehouse.objects.first()
        )

        order.remove_from_stock()
        self.assertEqual(product.variants.first().stock_quantity, 0)

    def test_order_should_remove_from_stock(self):
        order = Order(status=Order.REMOVE_FROM_STOCK_STATUS)
        self.assertTrue(order.should_remove_from_stock())

    def test_order_should_return_to_stock(self):
        order = Order(status=Order.RETURN_TO_STOCK_STATUS)
        self.assertTrue(order.should_return_to_stock())

    def test_order_should_remove_reservations(self):
        for status in Order.REMOVE_RESERVATIONS_STATUSES:
            order = Order(status=status)
            self.assertTrue(order.should_remove_reservations())

    def test_order_save(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), content_object=si,
                             quantity=3)

        order = Order.objects.create()
        OrderItem.objects.create(
            order=order, product_variant=variant, quantity=3, price=product.price, reserved=True,
            warehouse=Warehouse.objects.first()
        )

        order.status = Order.REMOVE_FROM_STOCK_STATUS
        order.save()

        self.assertEqual(product.variants.first().stock_quantity, 0)

        order.status = Order.RETURN_TO_STOCK_STATUS
        order.save()

        self.assertEqual(product.variants.first().stock_quantity, 3)

    def test_order_item_total(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), quantity=10,
                             content_object=si)

        order = Order.objects.create()
        item = OrderItem.objects.create(order=order, product_variant=variant, quantity=5, price=product.price,
                                        reserved=True)

        self.assertEqual(item.total(), 5 * product.price)

    def test_order_item_check_available_quantity(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), quantity=1,
                             content_object=si)

        order = Order.objects.create()

        with self.assertRaises(ValidationError):
            item = OrderItem(order=order, product_variant=variant, quantity=5, price=product.price,
                             reserved=True, warehouse=Warehouse.objects.first())
            item.check_available_quantity()

    def test_order_item_check_reserved_items(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, quantity=3, warehouse=Warehouse.objects.first(),
                             content_object=si)

        order = Order.objects.create(status=Order.REQUIRE_RESERVED_ITEMS_STATUSES[0])

        with self.assertRaises(ValidationError):
            item = OrderItem(order=order, product_variant=variant, quantity=3, price=product.price,
                             reserved=False, warehouse=Warehouse.objects.first())
            item.check_reserved_items()

    def test_order_item_get_actual_price(self):
        product = Product.objects.first()
        variant = product.variants.first()

        si = StockImport.objects.create()
        Stock.objects.create(product_variant=variant, warehouse=Warehouse.objects.first(), content_object=si,
                             quantity=4)

        order = Order.objects.create()
        item = OrderItem(order=order, product_variant=variant, quantity=3, price=product.price, discount_percentage=10,
                         reserved=False, warehouse=Warehouse.objects.first())

        self.assertEqual(item.get_actual_price(), item.price * (100 - 10) / 100)

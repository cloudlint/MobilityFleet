from datetime import datetime

import pytz
from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, F, Value, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.safestring import mark_safe
from django_cloud_storage.storage import CloudStorage
from django_cloud_thumbnails import ImageRatioField, ImageCropField
from djmoney.models.fields import MoneyField
from solo.models import SingletonModel


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=True, blank=True, unique=True)
    description = models.TextField(blank=True, null=True)
    seo_title = models.CharField(max_length=60, blank=True, null=True)
    seo_description = models.TextField(max_length=160, blank=True, null=True)
    seo_keywords = models.TextField(max_length=255, blank=True, null=True)
    seo_image = ImageCropField(blank=True, null=True, storage=CloudStorage)
    seo_image_cropping = ImageRatioField("seo_image", "1200x630")
    seo_image_cropped = models.ImageField(
        storage=CloudStorage, blank=True, null=True, editable=False
    )

    def discount_percentage(self):
        if not self.pk:
            return 0

        now = datetime.now(pytz.timezone(settings.TIME_ZONE))

        discount = self.discount_categories.filter(
            discount__active=True,
            discount__start_date__lte=now,
            discount__end_date__gte=now,
        ).first()

        if discount:
            return discount.percentage

        return 0

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Color(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "cities"


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "countries"


class Gender(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from="name", editable=True, blank=True, unique=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category, related_name="products", null=True, on_delete=models.SET_NULL
    )
    color = models.ForeignKey(Color, null=True, on_delete=models.SET_NULL)
    gender = models.ForeignKey(Gender, null=True, on_delete=models.SET_NULL)
    price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency=settings.ECOMMERCE_DEFAULT_CURRENCY,
        currency_choices=settings.ECOMMERCE_AVAILABLE_CURRENCIES,
    )
    seo_title = models.CharField(max_length=60, blank=True, null=True)
    seo_description = models.TextField(max_length=160, blank=True, null=True)
    seo_keywords = models.TextField(max_length=255, blank=True, null=True)
    seo_image = ImageCropField(blank=True, null=True, storage=CloudStorage)
    seo_image_cropping = ImageRatioField("seo_image", "1200x630")
    seo_image_cropped = models.ImageField(
        storage=CloudStorage, blank=True, null=True, editable=False
    )

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)

        self.discount = self.discount_percentage()
        self.has_discount = self.discount > 0
        self.actual_price = self.get_actual_price()
        self.is_on_stock = self.get_is_on_stock()

    def discount_percentage(self):
        now = datetime.now(pytz.timezone(settings.TIME_ZONE))

        if self.pk:
            discount = self.discount_products.filter(
                discount__active=True,
                discount__start_date__lte=now,
                discount__end_date__gte=now,
            ).first()

            if discount:
                return discount.percentage

        if self.category:
            return self.category.discount_percentage()

        return 0

    def get_actual_price(self):
        if not self.price:
            return 0

        return self.price * (100 - self.discount) / 100

    def get_is_on_stock(self):
        if self.pk:
            for variant in self.variants.all():
                if variant.available_quantity > 0:
                    return True

        return False


class ProductVariantManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                stock_quantity=Coalesce(
                    Subquery(
                        Stock.objects.filter(product_variant=OuterRef("pk"))
                        .values("product_variant")
                        .annotate(total_stock=Sum("quantity"))
                        .values("total_stock")[:1]
                    ),
                    Value(0),
                    output_field=IntegerField(),
                ),
                reserved_quantity=Coalesce(
                    Subquery(
                        OrderItem.objects.filter(
                            product_variant=OuterRef("pk"), reserved=True
                        )
                        .values("product_variant")
                        .annotate(total_reserved=Sum("quantity"))
                        .values("total_reserved")[:1]
                    ),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )
            .annotate(available_quantity=F("stock_quantity") - F("reserved_quantity"))
        )


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product, related_name="variants", on_delete=models.CASCADE
    )
    sku = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    objects = ProductVariantManager()

    reserved_quantity = 0
    stock_quantity = 0
    available_quantity = 0

    def save(self, *args, **kwargs):
        self.sku = self.sku.upper()

        super().save(*args, **kwargs)

    def stock_data(self) -> list[tuple[str, int]]:
        result = []

        rows = self.stock.values("warehouse_id").annotate(total=Sum("quantity"))

        for row in rows:
            warehouse = Warehouse.objects.get(pk=row["warehouse_id"])
            result.append((warehouse.name, row["total"]))

        return result

    def reservations_data(self) -> list[tuple[str, int]]:
        result = []

        for item in self.order_items.filter(reserved=True).all():
            result.append((item.order.code, item.quantity))

        return result

    def __str__(self):
        return self.sku


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = ImageCropField(blank=True, null=True, storage=CloudStorage)
    cropping = ImageRatioField("image", "1000x1000")
    cropped = models.ImageField(
        storage=CloudStorage, blank=True, null=True, editable=False
    )
    position = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.product} ({self.position})"


class Warehouse(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Stock(models.Model):
    product_variant = models.ForeignKey(
        ProductVariant, related_name="stock", on_delete=models.CASCADE
    )
    warehouse = models.ForeignKey(
        Warehouse, related_name="stock", on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True)

    def content_object_class(self):
        if self.content_type:
            return self.content_type.model_class()._meta.verbose_name.capitalize()

    def content_object_link(self):
        if self.content_type:
            url = reverse(
                f"admin:{self.content_type.app_label}_{self.content_type.model}_change",
                args=[self.object_id],
            )

            return mark_safe(f'<a href="{url}">{self.content_object_class()}</a>')

    content_object_link.short_description = "Source"

    class Meta:
        verbose_name_plural = "stock"

        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.product_variant.product.name} ({self.warehouse.name}) ({self.quantity})"


class StockImport(models.Model):
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    items = GenericRelation(Stock)

    def __str__(self):
        tz = timezone.get_current_timezone()

        return self.created_at.astimezone(tz).strftime("%d/%m/%Y %H:%M")


class Setting(SingletonModel):
    shipping_enabled = models.BooleanField(default=False)
    shipping_amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        default=0,
        null=True,
        blank=True,
        default_currency=settings.ECOMMERCE_DEFAULT_CURRENCY,
        currency_choices=settings.ECOMMERCE_AVAILABLE_CURRENCIES,
    )
    free_shipping_enabled = models.BooleanField(default=False)
    free_shipping_min_amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        default=0,
        blank=True,
        null=True,
        default_currency=settings.ECOMMERCE_DEFAULT_CURRENCY,
        currency_choices=settings.ECOMMERCE_AVAILABLE_CURRENCIES,
    )

    def __str__(self):
        return "Settings"

    class Meta:
        verbose_name = "Settings"


def generate_order_code():
    code = get_random_string(6).upper()

    try:
        Order.objects.get(code=code)
        return generate_order_code()
    except Order.DoesNotExist:
        return code


class Order(models.Model):
    ORDER_STATUSES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
        ("sent", "Sent"),
        ("returned", "Returned"),
        ("delivered", "Delivered"),
    )

    ALLOWED_STATUS_CHANGES = {
        "pending": ("confirmed", "canceled", "sent", "delivered"),
        "confirmed": ("canceled", "sent", "delivered"),
        "canceled": (),
        "sent": ("returned",),
        "returned": (),
        "delivered": ("returned",),
    }

    REMOVE_FROM_STOCK_STATUS = "delivered"

    RETURN_TO_STOCK_STATUS = "returned"

    REQUIRE_RESERVED_ITEMS_STATUSES = ("confirmed", "sent")

    REMOVE_RESERVATIONS_STATUSES = ("canceled", "returned", "delivered")

    CAN_MODIFY_ORDER_ITEMS_STATUSES = ("pending", "confirmed", "sent")

    code = models.CharField(
        max_length=16, blank=True, default=generate_order_code, db_index=True
    )
    status = models.CharField(
        max_length=16, choices=ORDER_STATUSES, default=ORDER_STATUSES[0][0]
    )
    email = models.EmailField(max_length=255, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    remark = models.TextField(blank=True, null=True)
    shipping_amount = MoneyField(
        max_digits=14,
        decimal_places=2,
        blank=True,
        null=True,
        default=0,
        default_currency=settings.ECOMMERCE_DEFAULT_CURRENCY,
        currency_choices=settings.ECOMMERCE_AVAILABLE_CURRENCIES,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    __original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.status

    def total_amount(self):
        total = self.shipping_amount

        for item in self.items.all():
            total += item.actual_price * item.quantity

        return total

    def total_quantity(self):
        quantity = 0

        for item in self.items.all():
            quantity += item.quantity

        return quantity

    def require_reserved_items(self):
        return self.status in self.REQUIRE_RESERVED_ITEMS_STATUSES

    def can_modify_order_items(self):
        if not self.pk:
            return True

        return self.status in self.CAN_MODIFY_ORDER_ITEMS_STATUSES

    def status_changed(self):
        return self.__original_status != self.status

    def check_status(self):
        if self.status_changed() and self.__original_status:
            allowed_statuses = self.ALLOWED_STATUS_CHANGES[self.__original_status]

            if not allowed_statuses:
                raise ValidationError(
                    f"Status of order with  status {self.__original_status} cannot be changed."
                )

            if self.status not in allowed_statuses:
                statuses = ", ".join(allowed_statuses)
                raise ValidationError(
                    f"Order with status {self.__original_status} can only be changed to {statuses}"
                )

    def remove_reservations(self):
        for item in self.items.all():
            item.reserved = False
            item.save()

    def return_to_stock(self):
        for item in self.items.all():
            stock = Stock(
                product_variant=item.product_variant,
                warehouse=item.warehouse,
                quantity=item.quantity,
                content_object=self,
            )
            stock.save()

    def remove_from_stock(self):
        for item in self.items.all():
            stock = Stock(
                product_variant=item.product_variant,
                warehouse=item.warehouse,
                quantity=-item.quantity,
                content_object=self,
            )
            stock.save()

    def clean(self):
        self.check_status()

    def should_remove_from_stock(self):
        return self.status == self.REMOVE_FROM_STOCK_STATUS

    def should_return_to_stock(self):
        return self.status == self.RETURN_TO_STOCK_STATUS

    def should_remove_reservations(self):
        return self.status in self.REMOVE_RESERVATIONS_STATUSES

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.status_changed():
            if self.should_return_to_stock():
                self.return_to_stock()
            elif self.should_remove_from_stock():
                self.remove_from_stock()

            if self.should_remove_reservations():
                self.remove_reservations()

    def __str__(self):
        return self.code


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_variant = models.ForeignKey(
        ProductVariant, related_name="order_items", on_delete=models.CASCADE
    )
    price = MoneyField(
        max_digits=14,
        decimal_places=2,
        default_currency=settings.ECOMMERCE_DEFAULT_CURRENCY,
        currency_choices=settings.ECOMMERCE_AVAILABLE_CURRENCIES,
    )
    discount_percentage = models.PositiveIntegerField(default=0, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    warehouse = models.ForeignKey(
        Warehouse, related_name="order_items", on_delete=models.SET_NULL, null=True
    )
    reserved = models.BooleanField(default=False)

    def total(self):
        return self.actual_price * self.quantity

    def check_available_quantity(self):
        if self.warehouse:

            try:
                total_quantity = self.quantity

                items = OrderItem.objects.filter(
                    warehouse=self.warehouse,
                    product_variant=self.product_variant,
                    reserved=True,
                ).all()

                for item in items:
                    if item.pk == self.pk:
                        continue

                    total_quantity += item.quantity

                self.product_variant.stock.filter(
                    quantity__gte=total_quantity, warehouse=self.warehouse
                ).get()
            except Stock.DoesNotExist:
                raise ValidationError(
                    "Selected warehouse does not have enough quantity of this item on stock."
                )

    def __init__(self, *args, **kwargs):
        super(OrderItem, self).__init__(*args, **kwargs)

        self.has_discount = self.discount_percentage > 0
        self.actual_price = self.get_actual_price()

    def check_reserved_items(self):
        if self.order.require_reserved_items() and not self.reserved:
            raise ValidationError(
                f"Order items must be reserved to change the status to {self.order.status}"
            )

    def clean(self):
        self.check_reserved_items()
        self.check_available_quantity()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_actual_price(self):
        if not self.price:
            return 0

        return self.price * (100 - int(self.discount_percentage)) / 100

    def __str__(self):
        return "Order item"


class Discount(models.Model):
    active = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    last_activation_run = models.DateTimeField(null=True, blank=True)
    last_deactivation_run = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class DiscountCategory(models.Model):
    discount = models.ForeignKey(
        Discount, related_name="categories", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        Category, related_name="discount_categories", on_delete=models.CASCADE
    )
    percentage = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "discount categories"

    def __str__(self):
        return self.category.name


class DiscountProduct(models.Model):
    discount = models.ForeignKey(
        Discount, related_name="products", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="discount_products", on_delete=models.CASCADE
    )
    percentage = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.product.name

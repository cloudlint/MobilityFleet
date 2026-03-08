from adminsortable2.admin import SortableTabularInline, SortableAdminBase
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.forms import ModelForm
from django_cloud_thumbnails import ImageCroppingMixin
from solo.admin import SingletonModelAdmin

from .models import (
    ProductImage,
    Gender,
    Category,
    Color,
    Product,
    ProductVariant,
    Stock,
    Warehouse,
    Setting,
    Order,
    OrderItem,
    StockImport,
    City,
    DiscountCategory,
    DiscountProduct,
    Discount,
    Country,
)


class ProductImageInline(ImageCroppingMixin, SortableTabularInline):
    model = ProductImage
    ordering = ["position"]


class AlwaysChangedModelForm(ModelForm):
    def has_changed(self):
        return True


class ProductVariantInline(SortableTabularInline):
    model = ProductVariant
    form = AlwaysChangedModelForm

    fields = (
        "sku",
        "name",
        "stock_data",
        "reservations_data",
        "available_quantity",
        "active",
    )
    readonly_fields = ["id", "stock_data", "reservations_data", "available_quantity"]
    extra = 0
    ordering = ["position"]
    search_fields = ["product"]

    def stock_data(self, obj: ProductVariant):
        data = obj.stock_data()

        return ", ".join([f"{x[1]} ({x[0]})" for x in data]) if data else "-"

    stock_data.short_description = "Stock"

    def reservations_data(self, obj: ProductVariant):
        data = obj.reservations_data()

        return ", ".join([f"{x[1]} ({x[0]})" for x in data]) if data else "-"

    reservations_data.short_description = "Reservations"

    def available_quantity(self, obj: ProductVariant):
        return obj.available_quantity if obj.available_quantity else "-"

    available_quantity.short_description = "Available quantity"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    fields = ["sku", "product", "name", "active"]

    def has_module_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        fields = ["id"]

        if obj and obj.pk:
            fields += ["sku", "product", "name"]

        return fields

    search_fields = ["sku", "name"]


@admin.register(Product)
class ProductAdmin(ImageCroppingMixin, SortableAdminBase, admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
    list_display = ("name", "slug", "category", "price")

    search_fields = ["name"]
    list_filter = ["category", "gender", "color"]

    fieldsets = [
        (
            "General information",
            {
                "fields": ["category", "color", "gender", "price"],
            },
        ),
        (
            "Web page details",
            {
                "fields": ["slug", "name", "description"],
            },
        ),
        (
            "SEO",
            {
                "fields": [
                    "seo_title",
                    "seo_description",
                    "seo_keywords",
                    "seo_image",
                    "seo_image_cropping",
                ],
            },
        ),
    ]

    def get_readonly_fields(self, request, obj=None):
        fields = []

        if obj and obj.pk:
            fields.append("sku")

        return fields


@admin.register(Category)
class CategoryAdmin(ImageCroppingMixin, admin.ModelAdmin):
    list_display = ["name"]

    fieldsets = [
        (
            "Web page details",
            {
                "fields": ["slug", "name", "description"],
            },
        ),
        (
            "SEO",
            {
                "fields": [
                    "seo_title",
                    "seo_description",
                    "seo_keywords",
                    "seo_image",
                    "seo_image_cropping",
                ],
            },
        ),
    ]


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = [
        "product_variant",
        "warehouse",
        "quantity",
        "content_object_link",
        "created_at",
    ]
    ordering = ["-created_at"]
    search_fields = ["product_variant__sku", "product_variant__name"]
    list_filter = ["quantity", "warehouse"]


class StockInline(GenericTabularInline):
    model = Stock
    extra = 0
    autocomplete_fields = ["warehouse", "product_variant"]


@admin.register(StockImport)
class StockImport(admin.ModelAdmin):
    inlines = [StockInline]
    ordering = ["-created_at"]
    list_display = ["created_at", "comment"]


@admin.register(Setting)
class SettingAdmin(ImageCroppingMixin, SingletonModelAdmin):
    fieldsets = [
        (
            "Shipping",
            {
                "fields": [
                    "shipping_enabled",
                    "shipping_amount",
                    "free_shipping_enabled",
                    "free_shipping_min_amount",
                ],
            },
        ),
    ]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    def has_change_permission(self, request, obj=None):
        return not obj or obj.can_modify_order_items()

    def has_delete_permission(self, request, obj=None):
        return not obj or obj.can_modify_order_items()

    def has_add_permission(self, request, obj):
        return not obj or obj.can_modify_order_items()

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(OrderItemInline, self).get_formset(request, obj, **kwargs)
        field = formset.form.base_fields["warehouse"]
        field.widget.can_add_related = False
        field.widget.can_change_related = False
        field.widget.can_delete_related = False

        return formset


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        to_field_name="name",
        widget=forms.Select,
        required=False,
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        to_field_name="name",
        widget=forms.Select,
        required=False,
    )


def get_shipping_fields():
    if hasattr(settings, "ECOMMERCE_SHIPPING_ADMIN_FIELDS"):
        return getattr(settings, "ECOMMERCE_SHIPPING_ADMIN_FIELDS")

    return [
        "full_name",
        "address",
        "city",
        "zip_code",
        "country",
        "phone",
        "remark",
        "shipping_amount",
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    inlines = [OrderItemInline]
    list_display = ["code", "status", "full_name", "created_at"]
    list_filter = ["status"]
    search_fields = ["code", "full_name"]
    readonly_fields = ["code", "total_amount", "created_at", "items"]

    fieldsets = [
        (
            "General information",
            {
                "fields": ["code", "created_at", "total_amount", "status", "email"],
            },
        ),
        ("Shipping", {"fields": get_shipping_fields()}),
    ]


class DiscountCategoryInline(admin.TabularInline):
    model = DiscountCategory
    extra = 0


class DiscountProductInline(admin.TabularInline):
    model = DiscountProduct
    extra = 0


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    inlines = [DiscountCategoryInline, DiscountProductInline]
    readonly_fields = ["last_activation_run", "last_deactivation_run"]

    def save_model(self, request, obj, form, change):
        # If this is an update, check if tracked fields have changed
        if change and obj.pk:
            try:
                original = Discount.objects.get(pk=obj.pk)
                # Check if name, start_date, or end_date have changed
                if (
                    original.name != obj.name
                    or original.start_date != obj.start_date
                    or original.end_date != obj.end_date
                ):
                    obj.last_activation_run = None
                    obj.last_deactivation_run = None
            except Discount.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # Check if DiscountCategory or DiscountProduct formsets have changed
        inline_changed = False
        for formset in formsets:
            if formset.model in [DiscountCategory, DiscountProduct]:
                if formset.has_changed():
                    inline_changed = True
                    break

        # If inlines changed, reset the activation/deactivation run fields
        if inline_changed and form.instance.pk:
            form.instance.last_activation_run = None
            form.instance.last_deactivation_run = None
            # Save only these fields to avoid triggering additional logic
            form.instance.save(
                update_fields=["last_activation_run", "last_deactivation_run"]
            )

        super().save_related(request, form, formsets, change)

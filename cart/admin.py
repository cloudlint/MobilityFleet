from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'product_name', 'product_price', 'quantity', 'subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'total_amount', 'item_count', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__username', 'billing_email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'item_count')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'total_amount', 'created_at', 'updated_at')
        }),
        ('Billing Information', {
            'fields': ('billing_first_name', 'billing_last_name', 'billing_email', 'billing_phone', 
                      'billing_address', 'billing_city', 'billing_postal_code', 'billing_province')
        }),
        ('Shipping Information', {
            'fields': ('shipping_first_name', 'shipping_last_name', 'shipping_address', 
                      'shipping_city', 'shipping_postal_code', 'shipping_province'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'product_price', 'subtotal')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__order_number', 'product_name')
    readonly_fields = ('subtotal',)
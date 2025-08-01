from django.contrib import admin
from .models import Store, Scooter, Parts, StockTransfer, StockTransferItem, ScooterMaintenanceHistory

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'contact_person', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'location', 'contact_person')

@admin.register(Scooter)
class ScooterAdmin(admin.ModelAdmin):
    list_display = ('vin', 'make', 'model', 'year', 'color', 'status', 'store')
    list_filter = ('status', 'store', 'make', 'year')
    search_fields = ('vin', 'make', 'model')
    date_hierarchy = 'purchase_date'

@admin.register(Parts)
class PartsAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'name', 'current_stock', 'reorder_level', 'store', 'unit_price', 'category')
    list_filter = ('store', 'category')
    search_fields = ('part_number', 'name', 'description')
    fieldsets = (
        (None, {
            'fields': ('part_number', 'name', 'description', 'store', 'category')
        }),
        ('Stock Information', {
            'fields': ('current_stock', 'reorder_level', 'unit_price', 'location_in_store')
        }),
    )

class StockTransferItemInline(admin.TabularInline):
    model = StockTransferItem
    extra = 1
    fields = ('part', 'quantity')

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_number', 'source_store', 'destination_store', 'get_total_items', 'status', 'transfer_date')
    list_filter = ('status', 'source_store', 'destination_store', 'transfer_date')
    search_fields = ('transfer_number', 'notes')
    date_hierarchy = 'transfer_date'
    inlines = [StockTransferItemInline]
    fieldsets = (
        (None, {
            'fields': ('transfer_number',)
        }),
        ('Store Information', {
            'fields': ('source_store', 'destination_store', 'transfer_date')
        }),
        ('Status Information', {
            'fields': ('status', 'notes', 'created_by')
        }),
    )
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'

@admin.register(ScooterMaintenanceHistory)
class ScooterMaintenanceHistoryAdmin(admin.ModelAdmin):
    list_display = ('scooter', 'maintenance_date', 'performed_by', 'cost', 'mileage_at_service')
    list_filter = ('maintenance_date', 'performed_by')
    search_fields = ('scooter__vin', 'scooter__make', 'scooter__model', 'description')
    date_hierarchy = 'maintenance_date'

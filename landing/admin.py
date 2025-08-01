from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Brand, Product, RentalCategory, RestorationGallery

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'image')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('is_active',)

class FeaturedProductFilter(admin.SimpleListFilter):
    title = 'Featured Status'
    parameter_name = 'featured_status'
    
    def lookups(self, request, model_admin):
        return (
            ('featured', 'Featured Products'),
            ('not_featured', 'Not Featured Products'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'featured':
            return queryset.filter(is_featured=True)
        if self.value() == 'not_featured':
            return queryset.filter(is_featured=False)
        return queryset

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'brand', 'stock', 'featured_status', 'is_active')
    list_filter = (FeaturedProductFilter, 'is_active', 'category', 'brand')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active',)
    actions = ['make_featured', 'remove_featured']
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Main Image', {
            'fields': ('image', 'image_url'),
            'description': 'Upload an image file or provide a URL for the main product image'
        }),
        ('Thumbnail Images', {
            'fields': ('thumbnail_1', 'thumbnail_2', 'thumbnail_3', 'thumbnail_4'),
            'description': 'Provide URLs for the 4 small thumbnail images displayed below the main image',
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('price', 'sale_price')
        }),
        ('Organization', {
            'fields': ('category', 'brand', 'stock')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
    )
    
    def featured_status(self, obj):
        if obj.is_featured:
            return format_html('<span style="background-color:#28a745; color:white; padding:5px 10px; border-radius:5px;">Featured</span>')
        return format_html('<span style="background-color:#6c757d; color:white; padding:5px 10px; border-radius:5px;">Not Featured</span>')
    
    featured_status.short_description = 'Featured'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} products have been marked as featured.')
    make_featured.short_description = "Mark selected products as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} products have been removed from featured.')
    remove_featured.short_description = "Remove selected products from featured"

class RentalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview', 'daily_rate', 'weekly_rate', 'monthly_rate', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    list_filter = ('is_active',)
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Card Image', {
            'fields': ('image', 'image_preview'),
            'description': 'Provide a URL for the rental category card image. This image will be displayed on the "Rent a Scooter" page.'
        }),
        ('Pricing', {
            'fields': ('daily_rate', 'weekly_rate', 'monthly_rate')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def image_preview(self, obj):
        """Display a preview of the rental category image"""
        if obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="max-width: 150px; max-height: 100px; border-radius: 5px; border: 1px solid #ddd; padding: 2px;" />',
                obj.get_image_url(),
                obj.name
            )
        return format_html('<span style="color: #999; font-style: italic;">No image provided</span>')
    
    image_preview.short_description = 'Image Preview'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(RentalCategory, RentalCategoryAdmin)

class RestorationGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_full_title', 'restoration_type', 'featured_status', 'is_active', 'date_completed')
    list_filter = ('restoration_type', 'is_featured', 'is_active', 'make', 'date_completed')
    search_fields = ('title', 'make', 'model', 'description')
    list_editable = ('is_active',)
    actions = ['make_featured', 'remove_featured']
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        ('Scooter Details', {
            'fields': ('year', 'make', 'model', 'restoration_type'),
            'classes': ('collapse',)
        }),
        ('Images', {
            'fields': ('before_image', 'after_image'),
            'description': 'Provide URLs for the before and after restoration images'
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active', 'date_completed')
        }),
    )
    
    def featured_status(self, obj):
        if obj.is_featured:
            return format_html('<span style="background-color:#28a745; color:white; padding:5px 10px; border-radius:5px;">Featured</span>')
        return format_html('<span style="background-color:#6c757d; color:white; padding:5px 10px; border-radius:5px;">Not Featured</span>')
    
    featured_status.short_description = 'Featured'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} restoration projects have been marked as featured.')
    make_featured.short_description = "Mark selected projects as featured"
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} restoration projects have been removed from featured.')
    remove_featured.short_description = "Remove selected projects from featured"

admin.site.register(RestorationGallery, RestorationGalleryAdmin)



from .models import HomepageVideo

admin.site.register(HomepageVideo)



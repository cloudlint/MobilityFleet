from django.db import models
from django.utils.text import slugify
from django.urls import reverse
import os

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.CharField(max_length=255, blank=True, null=True, 
                           help_text="URL for the category image")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_image_url(self):
        """Returns the image URL or a placeholder"""
        if self.image:
            return self.image
        else:
            return f'/static/images/category-{self.slug}.jpg'
    
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.CharField(max_length=255, blank=True, null=True)  # Changed from ImageField to CharField
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.CharField(max_length=255, blank=True, null=True)  # Changed from ImageField to CharField
    # You can have an image URL instead of uploading an image
    image_url = models.CharField(max_length=255, blank=True, null=True, 
                               help_text="URL for the product image (used if no image is uploaded)")
    
    # Thumbnail images
    thumbnail_1 = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text="URL for the first thumbnail image")
    thumbnail_2 = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text="URL for the second thumbnail image")
    thumbnail_3 = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text="URL for the third thumbnail image")
    thumbnail_4 = models.CharField(max_length=255, blank=True, null=True, 
                                 help_text="URL for the fourth thumbnail image")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_added']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('landing:product_detail', args=[self.id])
    
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price
    
    def get_display_price(self):
        if self.is_on_sale():
            return self.sale_price
        return self.price
    
    def get_image_url(self):
        """Returns either the uploaded image URL or the provided image URL"""
        if self.image_url:
            return self.image_url
        elif self.image:
            # The image field might be storing a path rather than using ImageField
            if hasattr(self.image, 'url'):
                return self.image.url
            else:
                return self.image  # If it's storing a path directly
        else:
            # Default image if none provided
            return '/static/images/products/placeholder.jpg'
    
    def get_thumbnail_url(self, thumbnail_number):
        """Returns the URL for a specific thumbnail image or falls back to main image"""
        thumbnail_field_name = f'thumbnail_{thumbnail_number}'
        thumbnail_url = getattr(self, thumbnail_field_name, None)
        
        if thumbnail_url:
            return thumbnail_url
        else:
            # Fallback to main image if thumbnail not set
            return self.get_image_url()
    
    def get_all_thumbnails(self):
        """Returns a list of all thumbnail URLs for template iteration"""
        return [
            self.get_thumbnail_url(1),
            self.get_thumbnail_url(2),
            self.get_thumbnail_url(3),
            self.get_thumbnail_url(4),
        ]
    
    def __str__(self):
        return self.name


class RentalCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.CharField(max_length=255, blank=True, null=True, 
                           help_text="URL for the rental category card image (displayed on Rent page)")
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Rental Categories"
        ordering = ['daily_rate']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_image_url(self):
        """Returns the image URL or a placeholder"""
        if self.image:
            if hasattr(self.image, 'url'):
                return self.image.url
            else:
                return self.image
        else:
            return '/static/images/rental/placeholder.jpg'
    
    def __str__(self):
        return self.name


class RestorationGallery(models.Model):
    title = models.CharField(max_length=200, help_text="Title of the restoration project (e.g., '1972 Vespa Sprint')")
    description = models.TextField(blank=True, help_text="Description of the restoration work done")
    before_image = models.CharField(max_length=255, help_text="URL for the 'before restoration' image")
    after_image = models.CharField(max_length=255, help_text="URL for the 'after restoration' image")
    year = models.PositiveIntegerField(blank=True, null=True, help_text="Year of the scooter")
    make = models.CharField(max_length=100, blank=True, help_text="Make of the scooter (e.g., Vespa, Honda)")
    model = models.CharField(max_length=100, blank=True, help_text="Model of the scooter (e.g., Sprint, Elite)")
    restoration_type = models.CharField(
        max_length=50,
        choices=[
            ('cosmetic', 'Cosmetic Restoration'),
            ('mechanical', 'Mechanical Restoration'),
            ('full', 'Full Restoration'),
            ('custom', 'Custom Project'),
        ],
        default='full',
        help_text="Type of restoration performed"
    )
    is_featured = models.BooleanField(default=False, help_text="Show this restoration in the main gallery")
    is_active = models.BooleanField(default=True)
    date_completed = models.DateField(blank=True, null=True, help_text="Date when the restoration was completed")
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Restoration Gallery"
        ordering = ['-date_added']
    
    def get_before_image_url(self):
        """Returns the before image URL"""
        return self.before_image if self.before_image else '/static/images/restoration/placeholder-before.jpg'
    
    def get_after_image_url(self):
        """Returns the after image URL"""
        return self.after_image if self.after_image else '/static/images/restoration/placeholder-after.jpg'
    
    def get_full_title(self):
        """Returns a full title including year, make, and model if available"""
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.make:
            parts.append(self.make)
        if self.model:
            parts.append(self.model)
        
        if parts:
            return ' '.join(parts)
        return self.title
    
    def __str__(self):
        return self.title





class HomepageVideo(models.Model):
    title = models.CharField(max_length=200, help_text="Title for the homepage video")
    description = models.TextField(help_text="Short description for the video")
    video_file = models.FileField(upload_to='videos/', help_text="Upload video file (MP4 format recommended)")
    is_active = models.BooleanField(default=True, help_text="Whether this video is currently active on the homepage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Homepage Video"
        verbose_name_plural = "Homepage Videos"

    def __str__(self):
        return self.title



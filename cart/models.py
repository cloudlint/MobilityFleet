from django.db import models
from django.contrib.auth.models import User
from landing.models import Product
import uuid
import logging

logger = logging.getLogger(__name__)


class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(max_length=32, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Billing information
    billing_first_name = models.CharField(max_length=50)
    billing_last_name = models.CharField(max_length=50)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20, blank=True)
    billing_address = models.CharField(max_length=200)
    billing_city = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_province = models.CharField(max_length=100)
    
    # Shipping information (can be same as billing)
    shipping_first_name = models.CharField(max_length=50, blank=True)
    shipping_last_name = models.CharField(max_length=50, blank=True)
    shipping_address = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_province = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_status = self.status

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
            
        status_changed = False
        if self.pk and self.status != self._original_status:
            status_changed = True
            
        super().save(*args, **kwargs)
        
        if status_changed:
            self.send_status_update_email()
        self._original_status = self.status

    def send_status_update_email(self):
        try:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            from django.conf import settings
            
            subject = f"Order Status Update - #{self.order_number}"
            html_message = render_to_string('cart/email/order_status_update.html', {'order': self})
            plain_message = strip_tags(html_message)
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@scooterrentals.com')
            to = self.billing_email
            
            send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            logger.info(f"Order status update email sent successfully for order {self.order_number}")
        except Exception as e:
            logger.error(f"Failed to send status update email for order {self.order_number}: {e}", exc_info=True)

    def generate_order_number(self):
        """Generate a unique order number"""
        return f"ORD-{str(uuid.uuid4())[:8].upper()}"
    
    @property
    def item_count(self):
        """Get total number of items in the order"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def status_color(self):
        """Get Bootstrap color class for order status"""
        status_colors = {
            'pending': 'warning',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return status_colors.get(self.status, 'secondary')
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)  # Store name at time of order
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of order
    product_image = models.CharField(max_length=255, blank=True)  # Store image URL at time of order
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this order item"""
        if self.product_price is None:
            return 0
        return self.product_price * self.quantity
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} (Order: {self.order.order_number})"
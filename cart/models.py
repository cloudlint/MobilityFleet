from django.db import models
# from landing.models import Product

class CartItem(models.Model):
    """Model for cart items"""
    session_id = models.CharField(max_length=255)
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_id = models.IntegerField(null=True, blank=True)  # Temporary field
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.quantity} x Product #{self.product_id}"
    
    # def get_total_price(self):
    #     return self.product.price * self.quantity
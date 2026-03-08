import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scooterrentals.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from landing.models import Product
from cart.models import Order

def run_test():
    print("Starting e-commerce flow test...")
    client = Client()
    
    # Create or get user
    user, created = User.objects.get_or_create(username='testuser', email='test@example.com')
    if created:
        user.set_password('password')
        user.save()
        
    # Login
    client.login(username='testuser', password='password')
    
    # Get product
    product = Product.objects.filter(slug='test-scooter').first()
    if not product:
        print("Test product not found")
        return
        
    print(f"Adding product {product.name} to cart...")
    response = client.post(f'/cart/add/{product.id}/')
    print(f"Add to cart response: {response.status_code}")
    
    # Check cart
    response = client.get('/cart/')
    print(f"Cart view response: {response.status_code}")
    
    # Checkout
    print("Checking out...")
    checkout_data = {
        'email': 'test@example.com',
        'phone': '1234567890',
        'first_name': 'Test',
        'last_name': 'User',
        'address': '123 Test St',
        'city': 'Testville',
        'province': 'WC',
        'postal_code': '1234',
        'card_name': 'Test User',
        'card_number': '1111222233334444',
        'expiry_month': '12',
        'expiry_year': '2025',
        'cvv': '123',
    }
    
    response = client.post('/cart/checkout/', checkout_data)
    print(f"Checkout response: {response.status_code}")
    
    # Find order
    order = Order.objects.filter(user=user).order_by('-created_at').first()
    if order:
        print(f"Order created successfully: {order.order_number} with status {order.status}")
        
        # Test status update
        print("Testing order status update...")
        order.status = 'shipped'
        order.save()
        print(f"Order status updated to: {order.status}")
    else:
        print("Failed to find order after checkout")

if __name__ == '__main__':
    run_test()

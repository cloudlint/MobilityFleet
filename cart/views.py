from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from landing.models import Product
from .models import Order, OrderItem
import uuid

def get_cart_id(request):
    """Get or create a cart ID for the current session"""
    if 'cart_id' not in request.session:
        request.session['cart_id'] = str(uuid.uuid4())
    return request.session['cart_id']

def get_cart(request):
    """Get the current cart items from session"""
    cart_id = get_cart_id(request)
    cart = request.session.get('cart', {})
    return cart

def cart_add(request, product_id):
    """Add a product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart_id = get_cart_id(request)
    cart = request.session.get('cart', {})
    
    # Convert to string for session storage
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        # If product already in cart, increment quantity
        cart[product_id_str]['quantity'] += 1
    else:
        # Add product to cart
        cart[product_id_str] = {
            'quantity': 1,
            'price': float(product.price),
            'name': product.name,
            'image': product.get_image_url()
        }
    
    request.session['cart'] = cart
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"{product.name} added to your cart",
            'cart_count': sum(item['quantity'] for item in cart.values())
        })
    
    messages.success(request, f"{product.name} added to your cart")
    return redirect('landing:products')

def cart_remove(request, product_id):
    """Remove a product from cart"""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        messages.success(request, "Item removed from your cart")
    
    return redirect('cart:cart_detail')

def cart_update(request, product_id):
    """Update cart item quantity"""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0 and product_id_str in cart:
        cart[product_id_str]['quantity'] = quantity
        request.session['cart'] = cart
    
    return redirect('cart:cart_detail')

def cart_detail(request):
    """View the cart contents"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    # Convert cart from session format to a list of items
    for product_id, item_data in cart.items():
        subtotal = item_data['price'] * item_data['quantity']
        total += subtotal
        
        cart_items.append({
            'id': product_id,
            'name': item_data['name'],
            'quantity': item_data['quantity'],
            'price': item_data['price'],
            'subtotal': subtotal,
            'image': item_data['image']
        })
    
    return render(request, 'cart/cart_detail.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def checkout(request):
    """Checkout process"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    # If cart is empty, redirect to cart detail
    if not cart:
        messages.warning(request, "Your cart is empty")
        return redirect('cart:cart_detail')
    
    # Convert cart from session format to a list of items
    for product_id, item_data in cart.items():
        subtotal = item_data['price'] * item_data['quantity']
        total += subtotal
        
        cart_items.append({
            'id': product_id,
            'name': item_data['name'],
            'quantity': item_data['quantity'],
            'price': item_data['price'],
            'subtotal': subtotal,
            'image': item_data['image']
        })
    
    if request.method == 'POST':
        # Create the order in the database
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            billing_first_name=request.POST.get('billing_first_name', request.user.first_name or 'Customer'),
            billing_last_name=request.POST.get('billing_last_name', request.user.last_name or ''),
            billing_email=request.POST.get('billing_email', request.user.email),
            billing_phone=request.POST.get('billing_phone', ''),
            billing_address=request.POST.get('billing_address', '123 Default Street'),
            billing_city=request.POST.get('billing_city', 'Cape Town'),
            billing_postal_code=request.POST.get('billing_postal_code', '8001'),
            billing_province=request.POST.get('billing_province', 'Western Cape'),
            # Use billing address as shipping if not provided separately
            shipping_first_name=request.POST.get('shipping_first_name', request.POST.get('billing_first_name', request.user.first_name or 'Customer')),
            shipping_last_name=request.POST.get('shipping_last_name', request.POST.get('billing_last_name', '')),
            shipping_address=request.POST.get('shipping_address', request.POST.get('billing_address', '123 Default Street')),
            shipping_city=request.POST.get('shipping_city', request.POST.get('billing_city', 'Cape Town')),
            shipping_postal_code=request.POST.get('shipping_postal_code', request.POST.get('billing_postal_code', '8001')),
            shipping_province=request.POST.get('shipping_province', request.POST.get('billing_province', 'Western Cape')),
        )
        
        # Create order items
        for product_id, item_data in cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=item_data['name'],
                    product_price=item_data['price'],
                    product_image=item_data['image'],
                    quantity=item_data['quantity']
                )
            except Product.DoesNotExist:
                # Handle case where product was deleted after being added to cart
                continue
        
        # Clear the cart
        request.session['cart'] = {}
        messages.success(request, f"Your order #{order.order_number} has been placed successfully")
        
        return render(request, 'cart/checkout_success.html', {
            'cart_items': cart_items,
            'total': total,
            'order_id': order.order_number,
            'order': order
        })
    
    return render(request, 'cart/checkout.html', {
        'cart_items': cart_items,
        'total': total
    })
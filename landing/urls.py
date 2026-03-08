from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    # Main navigation pages
    path('', views.home, name='home'),
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('buy/', views.buy, name='buy'),
    path('rent/', views.rent, name='rent'),
    path('restore/', views.restore, name='restore'),
    path('service/', views.service, name='service'),
    path('contact/', views.contact, name='contact'),
    
    # Account related pages
    path('account/', views.account, name='account'),
    path('account/order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('account/update-profile/', views.update_profile, name='update_profile'),
    path('account/change-password/', views.change_password, name='change_password'),
    path('account/add-scooter/', views.add_scooter, name='add_scooter'),
    path('account/remove-scooter/<int:scooter_id>/', views.remove_scooter, name='remove_scooter'),
    
    # Additional pages
    path('terms/', views.terms, name='terms'),
    path('rental-terms/', views.rental_terms, name='rental_terms'),
    path('financing/', views.financing, name='financing'),
    path('maintenance-tips/', views.maintenance_tips, name='maintenance_tips'),
    path('restoration-gallery/', views.restoration_gallery, name='restoration_gallery'),
]
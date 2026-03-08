"""
URL configuration for scooterrentals project.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from landing import views as landing_views
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('landing.urls')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('inventory/', include('inventory.urls')),
    path('service/', include('service.urls')),
    path('customers/', include('customers.urls')),
    path('analytics/', include('analytics.urls')),
    path('users/', include('users.urls', namespace='users')),
    path('staff-login/', landing_views.staff_login_view, name='staff_login'),
    path('password-reset-confirm/<uidb64>/<token>/', landing_views.password_reset_confirm, name='password_reset_confirm'),
    path('profile/', users_views.staff_profile, name='profile'),
    path('settings/', users_views.staff_settings, name='settings'),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

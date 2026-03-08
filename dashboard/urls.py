from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='index'),
    # Logout is handled by landing app to avoid duplicate messages
    path('api/scooter-counts/', views.get_scooter_counts, name='get_scooter_counts'),
    path('api/maintenance-jobcards/', views.get_maintenance_jobcards, name='get_maintenance_jobcards'),
]

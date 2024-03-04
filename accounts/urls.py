from django.urls import path
from .views import get_materials  # Import the get_materials view

urlpatterns = [
    # Other URL patterns
    path('get_materials/', get_materials, name='get_materials'),  # Define the URL pattern for get_materials
]

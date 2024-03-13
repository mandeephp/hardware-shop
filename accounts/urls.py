from django.urls import path
from .views import generate_pdf  # Import the get_materials view

urlpatterns = [
    # Other URL patterns
    path('generate-pdf/<int:purchase_id>/', generate_pdf, name='generate_pdf'),
]

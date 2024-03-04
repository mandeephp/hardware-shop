from django.shortcuts import render
from django.http import JsonResponse
from .models import Product


def get_materials(request):
    category_id = request.GET.get('category_id')
    materials = Product.objects.filter(product_category_id=category_id).values_list('id', 'product_name')
    return JsonResponse({'materials': dict(materials)})
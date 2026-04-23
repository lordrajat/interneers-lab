from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from products.api import (
    bulk_products_collection,
    categories_collection,
    category_detail,
    category_product_assignment,
    category_product_removal,
    normalize_product_brands,
    product_detail,
    products_collection,
)


def hello_name(request):
    name = request.GET.get("name", "World")
    return JsonResponse({"message": f"Hello, {name}!"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("hello/", hello_name),
    path("categories/", categories_collection),
    path("categories/<str:category_id>/", category_detail),
    path("categories/<str:category_id>/products/", category_product_assignment),
    path(
        "categories/<str:category_id>/products/<str:product_id>/",
        category_product_removal,
    ),
    path("products/", products_collection),
    path("products/bulk/", bulk_products_collection),
    path("products/normalize-brands/", normalize_product_brands),
    path("products/<str:product_id>/", product_detail),
]

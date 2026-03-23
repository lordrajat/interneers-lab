from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from products.views import product_detail, products_collection


def hello_name(request):
    name = request.GET.get("name", "World")
    return JsonResponse({"message": f"Hello, {name}!"})


urlpatterns = [
    path("admin/", admin.site.urls),
    path("hello/", hello_name),
    path("products/", products_collection),
    path("products/<str:product_id>/", product_detail),
]

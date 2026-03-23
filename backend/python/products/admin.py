from django.contrib import admin, messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from types import MethodType

from products.forms import ProductAdminForm
from products.services import ProductError, ProductService

product_service = ProductService()


def products_admin_list(request: HttpRequest) -> HttpResponse:
    context = {
        **admin.site.each_context(request),
        "title": "Products",
        "products": product_service.list_products()["products"],
        "add_url": reverse("admin:products_add"),
    }
    return TemplateResponse(request, "admin/products/product_list.html", context)


def products_admin_add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProductAdminForm(request.POST)
        if form.is_valid():
            try:
                product_service.create_product(form.cleaned_data)
            except ProductError as exc:
                form.add_error(None, exc.message)
            else:
                messages.success(request, "Product created successfully.")
                return redirect("admin:products_list")
    else:
        form = ProductAdminForm()

    context = {
        **admin.site.each_context(request),
        "title": "Add product",
        "form": form,
        "list_url": reverse("admin:products_list"),
    }
    return TemplateResponse(request, "admin/products/product_form.html", context)


original_get_urls = admin.site.get_urls


def get_admin_urls(self):
    custom_urls = [
        path(
            "products/",
            self.admin_view(products_admin_list),
            name="products_list",
        ),
        path(
            "products/add/",
            self.admin_view(products_admin_add),
            name="products_add",
        ),
    ]
    return custom_urls + original_get_urls()


admin.site.get_urls = MethodType(get_admin_urls, admin.site)

from django.http import HttpRequest, JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from products.api.common import error_response, parse_json_body
from products.domain.errors import ProductError
from products.services import ProductService

product_service = ProductService()

@csrf_exempt
@require_http_methods(["GET", "POST"])
def products_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        return JsonResponse(product_service.list_products(), status=200)

    try:
        payload = parse_json_body(request)
        product = product_service.create_product(payload)
    except ProductError as exc:
        return error_response(exc)

    return JsonResponse(product, status=201)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def bulk_products_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        return TemplateResponse(
            request,
            "products/bulk_upload.html",
            {"title": "Bulk Product Import"},
        )

    try:
        csv_file = request.FILES.get("file")
        if csv_file:
            csv_content = csv_file.read().decode("utf-8")
        else:
            csv_content = request.body.decode("utf-8")
        result = product_service.bulk_create_products_from_csv(csv_content)
    except UnicodeDecodeError:
        return JsonResponse({"error": "CSV body must be valid UTF-8 text."}, status=400)
    except ProductError as exc:
        return error_response(exc)

    return JsonResponse(result, status=201)


@csrf_exempt
@require_http_methods(["POST"])
def normalize_product_brands(request: HttpRequest) -> JsonResponse:
    try:
        payload = parse_json_body(request) if request.body else {}
        default_brand = payload.get("default_brand", "Unknown Brand")
        result = product_service.normalize_missing_brands(default_brand)
    except ProductError as exc:
        return error_response(exc)

    return JsonResponse(result, status=200)


@csrf_exempt
@require_http_methods(["POST"])
def category_product_assignment(request: HttpRequest, category_id: str) -> JsonResponse:
    try:
        payload = parse_json_body(request)
        product = product_service.add_product_to_category(category_id, payload)
    except ProductError as exc:
        return error_response(exc)

    return JsonResponse(product, status=200)


@csrf_exempt
@require_http_methods(["DELETE"])
def category_product_removal(
    request: HttpRequest, category_id: str, product_id: str
) -> JsonResponse:
    try:
        product = product_service.remove_product_from_category(category_id, product_id)
    except ProductError as exc:
        return error_response(exc)

    return JsonResponse(product, status=200)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def product_detail(request: HttpRequest, product_id: str) -> JsonResponse:
    try:
        if request.method == "GET":
            return JsonResponse(product_service.get_product(product_id), status=200)

        if request.method == "PUT":
            payload = parse_json_body(request)
            product = product_service.update_product(product_id, payload)
            return JsonResponse(product, status=200)

        product_service.delete_product(product_id)
        return JsonResponse({}, status=204)
    except ProductError as exc:
        return error_response(exc)

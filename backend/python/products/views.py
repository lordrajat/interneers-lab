import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from products.services import ProductError, ProductService

product_service = ProductService()


def _error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _parse_body(request: HttpRequest):
    if not request.body:
        raise ProductError("Request body is required.", 400)

    try:
        return json.loads(request.body)
    except json.JSONDecodeError as exc:
        raise ProductError("Invalid JSON body.", 400) from exc


@csrf_exempt
@require_http_methods(["GET", "POST"])
def products_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        return JsonResponse(product_service.list_products(), status=200)

    try:
        payload = _parse_body(request)
        product = product_service.create_product(payload)
    except ProductError as exc:
        return _error(exc.message, status=exc.status)

    return JsonResponse(product, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def product_detail(request: HttpRequest, product_id: str) -> JsonResponse:
    try:
        if request.method == "GET":
            return JsonResponse(product_service.get_product(product_id), status=200)

        if request.method == "PUT":
            payload = _parse_body(request)
            product = product_service.update_product(product_id, payload)
            return JsonResponse(product, status=200)

        product_service.delete_product(product_id)
        return JsonResponse({}, status=204)
    except ProductError as exc:
        return _error(exc.message, status=exc.status)

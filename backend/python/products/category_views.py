import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from products.category_services import CategoryService
from products.errors import ProductError

category_service = CategoryService()


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
def categories_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        return JsonResponse(category_service.list_categories(), status=200)

    try:
        payload = _parse_body(request)
        category = category_service.create_category(payload)
    except ProductError as exc:
        return _error(exc.message, status=exc.status)

    return JsonResponse(category, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def category_detail(request: HttpRequest, category_id: str) -> JsonResponse:
    try:
        if request.method == "GET":
            return JsonResponse(category_service.get_category(category_id), status=200)

        if request.method == "PUT":
            payload = _parse_body(request)
            category = category_service.update_category(category_id, payload)
            return JsonResponse(category, status=200)

        category_service.delete_category(category_id)
        return JsonResponse({}, status=204)
    except ProductError as exc:
        return _error(exc.message, status=exc.status)

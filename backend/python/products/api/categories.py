from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from products.api.common import error_response, parse_json_body
from products.domain.errors import ProductError
from products.services import CategoryService

category_service = CategoryService()

@csrf_exempt
@require_http_methods(["GET", "POST"])
def categories_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        return JsonResponse(category_service.list_categories(), status=200)

    try:
        payload = parse_json_body(request)
        category = category_service.create_category(payload)
    except ProductError as exc:
        return error_response(exc)

    return JsonResponse(category, status=201)


@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def category_detail(request: HttpRequest, category_id: str) -> JsonResponse:
    try:
        if request.method == "GET":
            return JsonResponse(category_service.get_category(category_id), status=200)

        if request.method == "PUT":
            payload = parse_json_body(request)
            category = category_service.update_category(category_id, payload)
            return JsonResponse(category, status=200)

        category_service.delete_category(category_id)
        return JsonResponse({}, status=204)
    except ProductError as exc:
        return error_response(exc)

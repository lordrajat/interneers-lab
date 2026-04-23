import json
from typing import Any

from django.http import HttpRequest, JsonResponse

from products.domain.errors import ProductError


def error_response(exc: ProductError) -> JsonResponse:
    return JsonResponse(exc.payload, status=exc.status)


def parse_json_body(request: HttpRequest) -> Any:
    if not request.body:
        raise ProductError("Request body is required.", 400)

    try:
        return json.loads(request.body)
    except json.JSONDecodeError as exc:
        raise ProductError("Invalid JSON body.", 400) from exc

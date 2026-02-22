import json
from itertools import count
from threading import Lock
from typing import Any

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


PRODUCTS: dict[int, dict[str, Any]] = {}
NEXT_ID = count(1)
STORE_LOCK = Lock()


def _error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _parse_body(request):
    try:
        data = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return None, _error("Invalid JSON body.")

    if not isinstance(data, dict):
        return None, _error("JSON body must be an object.")

    return data, None


def _validate_product_payload(payload: dict[str, Any], partial: bool = False):
    required_fields = ["name", "category", "price", "brand", "quantity"]
    string_fields = ["name", "description", "category", "brand"]

    if not partial:
        missing = [field for field in required_fields if field not in payload]
        if missing:
            return None, _error(f"Missing required fields: {', '.join(missing)}")

    product_data: dict[str, Any] = {}

    for field in string_fields:
        if field not in payload:
            continue

        value = payload[field]
        if not isinstance(value, str):
            return None, _error(f"Field '{field}' must be a string.")

        if field != "description" and not value.strip():
            return None, _error(f"Field '{field}' cannot be empty.")

        product_data[field] = value.strip() if field != "description" else value

    if "price" in payload:
        value = payload["price"]
        if not isinstance(value, (int, float)):
            return None, _error("Field 'price' must be a number.")
        if value < 0:
            return None, _error("Field 'price' must be >= 0.")
        product_data["price"] = round(float(value), 2)

    if "quantity" in payload:
        value = payload["quantity"]
        if not isinstance(value, int):
            return None, _error("Field 'quantity' must be an integer.")
        if value < 0:
            return None, _error("Field 'quantity' must be >= 0.")
        product_data["quantity"] = value

    if not partial and "description" not in product_data:
        product_data["description"] = ""

    return product_data, None


@csrf_exempt
def products_collection(request):
    if request.method == "GET":
        with STORE_LOCK:
            items = list(PRODUCTS.values())
        return JsonResponse({"products": items}, status=200)

    if request.method != "POST":
        return _error("Method not allowed.", status=405)

    payload, parse_error = _parse_body(request)
    if parse_error:
        return parse_error

    validated, validation_error = _validate_product_payload(payload, partial=False)
    if validation_error:
        return validation_error

    with STORE_LOCK:
        product_id = next(NEXT_ID)
        product = {"id": product_id, **validated}
        PRODUCTS[product_id] = product

    return JsonResponse(product, status=201)


@csrf_exempt
def product_detail(request, product_id: int):
    if request.method == "GET":
        with STORE_LOCK:
            product = PRODUCTS.get(product_id)
        if not product:
            return _error("Product not found.", status=404)
        return JsonResponse(product, status=200)

    if request.method == "PUT":
        payload, parse_error = _parse_body(request)
        if parse_error:
            return parse_error

        validated, validation_error = _validate_product_payload(payload, partial=True)
        if validation_error:
            return validation_error

        if not validated:
            return _error("At least one valid field is required for update.")

        with STORE_LOCK:
            existing = PRODUCTS.get(product_id)
            if not existing:
                return _error("Product not found.", status=404)
            existing.update(validated)
            product = dict(existing)

        return JsonResponse(product, status=200)

    if request.method == "DELETE":
        with STORE_LOCK:
            existed = PRODUCTS.pop(product_id, None)
        if not existed:
            return _error("Product not found.", status=404)
        return JsonResponse({}, status=204)

    return _error("Method not allowed.", status=405)

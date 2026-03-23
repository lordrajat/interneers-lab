from decimal import Decimal, InvalidOperation
from typing import Any

from products.repository import ProductRepository, serialize_product


class ProductError(Exception):
    def __init__(self, message: str, status: int) -> None:
        super().__init__(message)
        self.message = message
        self.status = status


class ProductService:
    def __init__(self, repository: ProductRepository | None = None) -> None:
        self.repository = repository or ProductRepository()

    def list_products(self) -> dict[str, Any]:
        products = [serialize_product(product) for product in self.repository.list_all()]
        return {"products": products}

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self._validate_product_payload(payload, partial=False)
        return serialize_product(self.repository.create(validated))

    def get_product(self, product_id: str) -> dict[str, Any]:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductError("Product not found.", 404)
        return serialize_product(product)

    def update_product(self, product_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self._validate_product_payload(payload, partial=True)
        if not validated:
            raise ProductError("At least one valid field is required for update.", 400)

        product = self.repository.update(product_id, validated)
        if not product:
            raise ProductError("Product not found.", 404)

        return serialize_product(product)

    def delete_product(self, product_id: str) -> None:
        if not self.repository.delete(product_id):
            raise ProductError("Product not found.", 404)

    def _validate_product_payload(self, payload: Any, partial: bool = False) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ProductError("JSON body must be an object.", 400)

        required_fields = ["name", "category", "price", "brand", "quantity"]
        string_fields = ["name", "description", "category", "brand"]

        if not partial:
            missing = [field for field in required_fields if field not in payload]
            if missing:
                raise ProductError(f"Missing required fields: {', '.join(missing)}", 400)

        product_data: dict[str, Any] = {}

        for field in string_fields:
            if field not in payload:
                continue

            product_data[field] = self._validate_string_field(
                field,
                payload[field],
                allow_empty=field == "description",
            )

        if "price" in payload:
            product_data["price"] = self._validate_price(payload["price"])

        if "quantity" in payload:
            product_data["quantity"] = self._validate_quantity(payload["quantity"])

        if not partial and "description" not in product_data:
            product_data["description"] = ""

        return product_data

    def _validate_string_field(self, field: str, value: Any, allow_empty: bool = False) -> str:
        if not isinstance(value, str):
            raise ProductError(f"Field '{field}' must be a string.", 400)

        if allow_empty:
            return value

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ProductError(f"Field '{field}' cannot be empty.", 400)

        return cleaned_value

    def _validate_price(self, value: Any) -> Decimal:
        if isinstance(value, bool):
            raise ProductError("Field 'price' must be a number.", 400)

        try:
            decimal_price = Decimal(str(value)).quantize(Decimal("0.01"))
        except (InvalidOperation, TypeError, ValueError):
            raise ProductError("Field 'price' must be a number.", 400) from None

        if decimal_price < 0:
            raise ProductError("Field 'price' must be >= 0.", 400)

        return decimal_price

    def _validate_quantity(self, value: Any) -> int:
        if not isinstance(value, int):
            raise ProductError("Field 'quantity' must be an integer.", 400)

        if value < 0:
            raise ProductError("Field 'quantity' must be >= 0.", 400)

        return value

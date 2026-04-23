from decimal import Decimal, InvalidOperation
from typing import Any

from bson import ObjectId

from products.domain.errors import ProductError
from products.repositories import CategoryRepository, ProductRepository, serialize_product
from products.services.bulk_import import BulkProductImportService


class ProductService:
    def __init__(
        self,
        repository: ProductRepository | None = None,
        category_repository: CategoryRepository | None = None,
    ) -> None:
        self.repository = repository or ProductRepository()
        self.category_repository = category_repository or CategoryRepository()
        self.bulk_import_service = BulkProductImportService(self)

    def list_products(self) -> dict[str, Any]:
        products = [serialize_product(product) for product in self.repository.list_all()]
        return {"products": products}

    def create_product(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self.validate_product_payload(payload, partial=False)
        return serialize_product(self.repository.create(validated))

    def get_product(self, product_id: str) -> dict[str, Any]:
        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductError("Product not found.", 404)
        return serialize_product(product)

    def update_product(self, product_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        existing_product = self.repository.get_by_id(product_id)
        if not existing_product:
            raise ProductError("Product not found.", 404)

        validated = self.validate_product_payload(payload, partial=True)
        if not validated:
            raise ProductError("At least one valid field is required for update.", 400)

        self._ensure_brand_present_for_existing_product(existing_product, validated)

        product = self.repository.update(product_id, validated)
        if not product:
            raise ProductError("Product not found.", 404)

        return serialize_product(product)

    def delete_product(self, product_id: str) -> None:
        if not self.repository.delete(product_id):
            raise ProductError("Product not found.", 404)

    def add_product_to_category(self, category_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        category = self._validate_category(category_id)
        product_id = payload.get("product_id")
        product = self._get_product_or_error(product_id)
        product.category = category
        return serialize_product(self.repository.save(product))

    def remove_product_from_category(self, category_id: str, product_id: str) -> dict[str, Any]:
        category = self._validate_category(category_id)
        product = self._get_product_or_error(product_id)

        if str(product.category.id) != str(category.id):
            raise ProductError("Product does not belong to this category.", 400)

        uncategorized, _ = self.category_repository.get_or_create(
            {
                "title": "Uncategorized",
                "description": "Fallback category for products removed from a category.",
            }
        )

        product.category = uncategorized
        return serialize_product(self.repository.save(product))

    def bulk_create_products_from_csv(self, csv_content: str) -> dict[str, Any]:
        return self.bulk_import_service.import_csv(csv_content)

    def normalize_missing_brands(self, default_brand: str = "Unknown Brand") -> dict[str, Any]:
        cleaned_brand = self._validate_string_field("brand", default_brand)
        updated_products = []

        for product in self.repository.list_missing_brand():
            product.brand = cleaned_brand
            updated_products.append(serialize_product(self.repository.save(product)))

        return {"updated_count": len(updated_products), "products": updated_products}

    def validate_product_payload(
        self, payload: Any, partial: bool = False
    ) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ProductError("JSON body must be an object.", 400)

        required_fields = ["name", "category_id", "price", "brand", "quantity"]
        string_fields = ["name", "description", "brand"]

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

        if "category_id" in payload:
            product_data["category"] = self._validate_category(payload["category_id"])

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

    def _validate_category(self, value: Any):
        if not isinstance(value, str) or not ObjectId.is_valid(value):
            raise ProductError("Field 'category_id' must be a valid category id.", 400)

        category = self.category_repository.get_by_id(value)
        if not category:
            raise ProductError("Category not found.", 404)

        return category

    def _get_product_or_error(self, product_id: Any):
        if not isinstance(product_id, str) or not ObjectId.is_valid(product_id):
            raise ProductError("Field 'product_id' must be a valid product id.", 400)

        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductError("Product not found.", 404)

        return product

    def _ensure_brand_present_for_existing_product(
        self, product, updates: dict[str, Any]
    ) -> None:
        existing_brand = (product.brand or "").strip()
        next_brand = updates.get("brand", existing_brand)

        if not next_brand:
            raise ProductError(
                "Existing product is missing a brand. Provide 'brand' or run the brand normalization endpoint.",
                400,
            )

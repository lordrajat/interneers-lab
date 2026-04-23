from typing import Any

from products.domain.errors import ProductError
from products.repositories import CategoryRepository, ProductRepository, serialize_category, serialize_product


class CategoryService:
    def __init__(
        self,
        repository: CategoryRepository | None = None,
        product_repository: ProductRepository | None = None,
    ) -> None:
        self.repository = repository or CategoryRepository()
        self.product_repository = product_repository or ProductRepository()

    def list_categories(self) -> dict[str, Any]:
        categories = [serialize_category(category) for category in self.repository.list_all()]
        return {"categories": categories}

    def create_category(self, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self._validate_category_payload(payload, partial=False)
        return serialize_category(self.repository.create(validated))

    def get_category(self, category_id: str) -> dict[str, Any]:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise ProductError("Category not found.", 404)

        products = [
            serialize_product(product)
            for product in self.product_repository.list_by_category(category)
        ]

        return {
            **serialize_category(category),
            "products": products,
            "product_count": len(products),
        }

    def update_category(self, category_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        validated = self._validate_category_payload(payload, partial=True)
        if not validated:
            raise ProductError("At least one valid field is required for update.", 400)

        category = self.repository.update(category_id, validated)
        if not category:
            raise ProductError("Category not found.", 404)

        return serialize_category(category)

    def delete_category(self, category_id: str) -> None:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise ProductError("Category not found.", 404)

        if self.product_repository.exists_for_category(category):
            raise ProductError("Cannot delete category while products still belong to it.", 400)

        self.repository.delete(category_id)

    def _validate_category_payload(self, payload: Any, partial: bool = False) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise ProductError("JSON body must be an object.", 400)

        required_fields = ["title"]

        if not partial:
            missing = [field for field in required_fields if field not in payload]
            if missing:
                raise ProductError(f"Missing required fields: {', '.join(missing)}", 400)

        category_data: dict[str, Any] = {}

        if "title" in payload:
            title = payload["title"]
            if not isinstance(title, str):
                raise ProductError("Field 'title' must be a string.", 400)

            cleaned_title = title.strip()
            if not cleaned_title:
                raise ProductError("Field 'title' cannot be empty.", 400)

            category_data["title"] = cleaned_title

        if "description" in payload:
            description = payload["description"]
            if not isinstance(description, str):
                raise ProductError("Field 'description' must be a string.", 400)
            category_data["description"] = description

        if not partial and "description" not in category_data:
            category_data["description"] = ""

        return category_data

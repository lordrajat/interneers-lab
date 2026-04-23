from typing import Any

from bson import ObjectId
from mongoengine.errors import ValidationError

from products.domain.models import ProductCategory


def serialize_category(category: ProductCategory) -> dict[str, Any]:
    return {
        "id": str(category.id),
        "title": category.title,
        "description": category.description,
        "created_at": category.created_at.isoformat() if category.created_at else None,
        "updated_at": category.updated_at.isoformat() if category.updated_at else None,
    }


class CategoryRepository:
    def create(self, data: dict[str, Any]) -> ProductCategory:
        category = ProductCategory(**data)
        category.save()
        return category

    def list_all(self) -> list[ProductCategory]:
        return list(ProductCategory.objects.order_by("title"))

    def get_by_id(self, category_id: str) -> ProductCategory | None:
        if not ObjectId.is_valid(category_id):
            return None
        return ProductCategory.objects(id=category_id).first()

    def get_by_title(self, title: str) -> ProductCategory | None:
        return ProductCategory.objects(title=title).first()

    def get_or_create(self, data: dict[str, Any]) -> tuple[ProductCategory, bool]:
        existing = self.get_by_title(data["title"])
        if existing:
            return existing, False

        return self.create(data), True

    def update(self, category_id: str, updates: dict[str, Any]) -> ProductCategory | None:
        category = self.get_by_id(category_id)
        if not category:
            return None

        for field, value in updates.items():
            setattr(category, field, value)

        try:
            category.save()
        except ValidationError:
            return None

        return category

    def delete(self, category_id: str) -> bool:
        category = self.get_by_id(category_id)
        if not category:
            return False

        category.delete()
        return True

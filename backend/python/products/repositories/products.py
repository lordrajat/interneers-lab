from typing import Any

from bson import ObjectId
from mongoengine.errors import ValidationError

from products.domain.models import Product, ProductCategory
from products.repositories.categories import serialize_category


def serialize_product(product: Product) -> dict[str, Any]:
    return {
        "id": str(product.id),
        "name": product.name,
        "description": product.description,
        "category": serialize_category(product.category),
        "price": float(product.price),
        "brand": product.brand,
        "quantity": product.quantity,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


class ProductRepository:
    def create(self, data: dict[str, Any]) -> Product:
        product = Product(**data)
        product.save()
        return product

    def list_all(self) -> list[Product]:
        return list(Product.objects.order_by("-created_at"))

    def list_by_category(self, category: ProductCategory) -> list[Product]:
        return list(Product.objects(category=category).order_by("-created_at"))

    def get_by_id(self, product_id: str) -> Product | None:
        if not ObjectId.is_valid(product_id):
            return None
        return Product.objects(id=product_id).first()

    def save(self, product: Product) -> Product:
        product.save()
        return product

    def update(self, product_id: str, updates: dict[str, Any]) -> Product | None:
        product = self.get_by_id(product_id)
        if not product:
            return None

        for field, value in updates.items():
            setattr(product, field, value)

        try:
            product.save()
        except ValidationError:
            return None

        return product

    def delete(self, product_id: str) -> bool:
        product = self.get_by_id(product_id)
        if not product:
            return False

        product.delete()
        return True

    def exists_for_category(self, category: ProductCategory) -> bool:
        return Product.objects(category=category).first() is not None

    def list_missing_brand(self) -> list[Product]:
        return list(Product.objects.filter(__raw__={"$or": [{"brand": {"$exists": False}}, {"brand": None}, {"brand": ""}]}))

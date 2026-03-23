from typing import Any

from bson import ObjectId
from mongoengine.errors import ValidationError

from products.models import Product


def serialize_product(product: Product) -> dict[str, Any]:
    return {
        "id": str(product.id),
        "name": product.name,
        "description": product.description,
        "category": product.category,
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

    def get_by_id(self, product_id: str) -> Product | None:
        if not ObjectId.is_valid(product_id):
            return None
        return Product.objects(id=product_id).first()

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

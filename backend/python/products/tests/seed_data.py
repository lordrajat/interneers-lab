from decimal import Decimal

from products.models import Product, ProductCategory


def seed_categories() -> dict[str, ProductCategory]:
    electronics = ProductCategory(title="Electronics", description="Devices and gadgets").save()
    office = ProductCategory(title="Office", description="Work essentials").save()
    return {"electronics": electronics, "office": office}


def seed_products(categories: dict[str, ProductCategory]) -> dict[str, Product]:
    laptop = Product(
        name="Laptop",
        description="16GB RAM",
        category=categories["electronics"],
        price=Decimal("899.99"),
        brand="Lenovo",
        quantity=12,
    ).save()
    keyboard = Product(
        name="Keyboard",
        description="Mechanical",
        category=categories["office"],
        price=Decimal("59.99"),
        brand="KeyCo",
        quantity=30,
    ).save()
    return {"laptop": laptop, "keyboard": keyboard}

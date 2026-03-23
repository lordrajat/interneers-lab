from datetime import datetime, timezone
from decimal import Decimal

from mongoengine import DateTimeField, DecimalField, Document, IntField, StringField


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Product(Document):
    meta = {"collection": "products"}

    name = StringField(required=True, max_length=120)
    description = StringField(default="")
    category = StringField(required=True, max_length=80)
    price = DecimalField(required=True, min_value=Decimal("0"), precision=2, force_string=True)
    brand = StringField(required=True, max_length=80)
    quantity = IntField(required=True, min_value=0)
    created_at = DateTimeField(default=_utc_now)
    updated_at = DateTimeField(default=_utc_now)

    def save(self, *args, **kwargs):
        self.updated_at = _utc_now()
        return super().save(*args, **kwargs)

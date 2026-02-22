from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=80)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    brand = models.CharField(max_length=80)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self) -> str:
        return f"{self.name} ({self.brand})"

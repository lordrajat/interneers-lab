import csv
import io
from typing import Any

from products.domain.errors import ProductError
from products.repositories import serialize_product


class BulkProductImportService:
    REQUIRED_COLUMNS = {
        "name",
        "description",
        "category_id",
        "price",
        "brand",
        "quantity",
    }

    def __init__(self, product_service) -> None:
        self.product_service = product_service

    def import_csv(self, csv_content: str) -> dict[str, Any]:
        if not csv_content.strip():
            raise ProductError("CSV body is required.", 400)

        try:
            reader = csv.DictReader(io.StringIO(csv_content))
        except csv.Error as exc:
            raise ProductError("Invalid CSV body.", 400) from exc

        if not reader.fieldnames:
            raise ProductError("CSV header row is required.", 400)

        missing_columns = sorted(self.REQUIRED_COLUMNS.difference(reader.fieldnames))
        if missing_columns:
            raise ProductError(
                f"Missing required CSV columns: {', '.join(missing_columns)}",
                400,
            )

        created_products = []
        row_errors = []

        for row_number, row in enumerate(reader, start=2):
            if not any((value or "").strip() for value in row.values()):
                continue

            try:
                payload = self._normalize_csv_row(row)
                validated = self.product_service.validate_product_payload(
                    payload, partial=False
                )
                created_products.append(
                    serialize_product(self.product_service.repository.create(validated))
                )
            except ProductError as exc:
                row_errors.append({"row": row_number, "error": exc.message})

        if row_errors:
            raise ProductError(
                "Bulk import failed.",
                400,
                payload={"message": "Bulk import failed.", "rows": row_errors},
            )

        return {"products": created_products, "created_count": len(created_products)}

    def _normalize_csv_row(self, row: dict[str, str]) -> dict[str, Any]:
        quantity = (row.get("quantity") or "").strip()
        try:
            parsed_quantity = int(quantity)
        except ValueError:
            raise ProductError("Field 'quantity' must be an integer.", 400) from None

        return {
            "name": (row.get("name") or "").strip(),
            "description": row.get("description") or "",
            "category_id": (row.get("category_id") or "").strip(),
            "price": (row.get("price") or "").strip(),
            "brand": (row.get("brand") or "").strip(),
            "quantity": parsed_quantity,
        }

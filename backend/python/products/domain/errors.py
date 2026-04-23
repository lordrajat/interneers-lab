from typing import Any


class ProductError(Exception):
    def __init__(
        self, message: str, status: int, payload: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.payload = payload or {"error": message}

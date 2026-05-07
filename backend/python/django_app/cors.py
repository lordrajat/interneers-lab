import os


class SimpleCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        origins = os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        )
        self.allowed_origins = {origin.strip() for origin in origins.split(",") if origin.strip()}

    def __call__(self, request):
        origin = request.headers.get("Origin")

        if request.method == "OPTIONS":
            response = self._preflight_response()
        else:
            response = self.get_response(request)

        if origin in self.allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response["Vary"] = "Origin"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"

        return response

    def _preflight_response(self):
        from django.http import HttpResponse

        return HttpResponse(status=204)

import os
from unittest import SkipTest

from django.conf import settings
from django.test import Client, SimpleTestCase
from mongoengine import connect, disconnect
from pymongo.errors import PyMongoError

from products.models import Product, ProductCategory


def _mongo_test_settings() -> dict[str, object]:
    default_cfg = settings.MONGODB_SETTINGS
    return {
        "db": os.getenv("MONGO_TEST_DB", "backenddb_integration_test"),
        "host": os.getenv("MONGO_TEST_HOST", str(default_cfg.get("host", "localhost"))),
        "port": int(os.getenv("MONGO_TEST_PORT", str(default_cfg.get("port", 27019)))),
        "username": os.getenv("MONGO_TEST_USER", str(default_cfg.get("username", "root"))),
        "password": os.getenv("MONGO_TEST_PASS", str(default_cfg.get("password", "example"))),
        "authentication_source": os.getenv(
            "MONGO_TEST_AUTH_SOURCE",
            str(default_cfg.get("authentication_source", "admin")),
        ),
        "serverSelectionTimeoutMS": 1200,
    }


class MongoIntegrationTestCase(SimpleTestCase):
    client: Client

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        disconnect(alias="default")
        cfg = _mongo_test_settings()
        try:
            connect(alias="default", **cfg)
            Product._get_db().client.admin.command("ping")
        except (PyMongoError, Exception) as exc:
            disconnect(alias="default")
            raise SkipTest(
                "Local MongoDB integration server is not reachable. "
                "Start it with `docker compose up -d` in `backend/python`."
            ) from exc

    @classmethod
    def tearDownClass(cls):
        disconnect(alias="default")
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        Product.drop_collection()
        ProductCategory.drop_collection()

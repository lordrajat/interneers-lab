import json

import mongomock
from django.test import Client, SimpleTestCase
from mongoengine import connect, disconnect

from products.models import Product


class ProductApiTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        disconnect(alias="default")
        connect(
            "products_test_db",
            alias="default",
            host="mongodb://localhost",
            mongo_client_class=mongomock.MongoClient,
        )

    @classmethod
    def tearDownClass(cls):
        disconnect(alias="default")
        super().tearDownClass()

    def setUp(self):
        self.client = Client()
        Product.drop_collection()
        self.base_payload = {
            "name": "Laptop",
            "description": "16GB RAM",
            "category": "Electronics",
            "price": 899.99,
            "brand": "Lenovo",
            "quantity": 14,
        }

    def test_create_product(self):
        response = self.client.post(
            "/products/",
            data=json.dumps(self.base_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIsInstance(body["id"], str)
        self.assertEqual(body["name"], "Laptop")
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

    def test_create_product_validation(self):
        invalid_payload = {
            "name": "",
            "category": "Electronics",
            "price": -10,
            "brand": "Lenovo",
            "quantity": -1,
        }

        response = self.client.post(
            "/products/",
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_create_product_invalid_json(self):
        response = self.client.post(
            "/products/",
            data='{"name": "Laptop"',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Invalid JSON body."})

    def test_list_get_update_delete_product(self):
        create_response = self.client.post(
            "/products/",
            data=json.dumps(self.base_payload),
            content_type="application/json",
        )
        product_id = create_response.json()["id"]

        list_response = self.client.get("/products/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()["products"]), 1)

        get_response = self.client.get(f"/products/{product_id}/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["brand"], "Lenovo")

        update_response = self.client.put(
            f"/products/{product_id}/",
            data=json.dumps({"quantity": 9, "price": 799.5}),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["quantity"], 9)

        delete_response = self.client.delete(f"/products/{product_id}/")
        self.assertEqual(delete_response.status_code, 204)

        get_deleted_response = self.client.get(f"/products/{product_id}/")
        self.assertEqual(get_deleted_response.status_code, 404)

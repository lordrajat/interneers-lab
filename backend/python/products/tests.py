import json
from itertools import count

from django.test import Client, TestCase

from products import views


class ProductApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        views.PRODUCTS.clear()
        views.NEXT_ID = count(1)
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
        self.assertEqual(body["id"], 1)
        self.assertEqual(body["name"], "Laptop")

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

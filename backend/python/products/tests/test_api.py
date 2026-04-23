import json

import mongomock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, SimpleTestCase
from mongoengine import connect, disconnect

from products.models import Product, ProductCategory


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
        ProductCategory.drop_collection()
        self.category = ProductCategory(title="Electronics", description="Devices").save()
        self.base_payload = {
            "name": "Laptop",
            "description": "16GB RAM",
            "category_id": str(self.category.id),
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
        self.assertEqual(body["category"]["id"], str(self.category.id))
        self.assertEqual(body["category"]["title"], "Electronics")
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

    def test_create_product_validation(self):
        invalid_payload = {
            "name": "",
            "category_id": str(self.category.id),
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

    def test_create_product_requires_brand(self):
        invalid_payload = {
            "name": "Laptop",
            "description": "16GB RAM",
            "category_id": str(self.category.id),
            "price": 899.99,
            "brand": "   ",
            "quantity": 14,
        }

        response = self.client.post(
            "/products/",
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Field 'brand' cannot be empty."})

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
        self.assertEqual(get_response.json()["category"]["title"], "Electronics")

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

    def test_category_crud(self):
        create_response = self.client.post(
            "/categories/",
            data=json.dumps({"title": "Kitchen Essentials", "description": "Home and kitchen"}),
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 201)
        category_id = create_response.json()["id"]

        list_response = self.client.get("/categories/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()["categories"]), 2)

        get_response = self.client.get(f"/categories/{category_id}/")
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["title"], "Kitchen Essentials")
        self.assertEqual(get_response.json()["products"], [])
        self.assertEqual(get_response.json()["product_count"], 0)

        update_response = self.client.put(
            f"/categories/{category_id}/",
            data=json.dumps({"description": "Updated"}),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["description"], "Updated")

        delete_response = self.client.delete(f"/categories/{category_id}/")
        self.assertEqual(delete_response.status_code, 204)

    def test_get_category_includes_products(self):
        create_response = self.client.post(
            "/products/",
            data=json.dumps(self.base_payload),
            content_type="application/json",
        )

        self.assertEqual(create_response.status_code, 201)

        response = self.client.get(f"/categories/{self.category.id}/")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["id"], str(self.category.id))
        self.assertEqual(body["title"], "Electronics")
        self.assertEqual(body["product_count"], 1)
        self.assertEqual(len(body["products"]), 1)
        self.assertEqual(body["products"][0]["name"], "Laptop")
        self.assertEqual(body["products"][0]["category"]["id"], str(self.category.id))

    def test_cannot_delete_category_with_products(self):
        self.client.post(
            "/products/",
            data=json.dumps(self.base_payload),
            content_type="application/json",
        )
        response = self.client.delete(f"/categories/{self.category.id}/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {"error": "Cannot delete category while products still belong to it."},
        )

    def test_can_move_product_into_category(self):
        office = ProductCategory(title="Office", description="Work items").save()
        create_response = self.client.post(
            "/products/",
            data=json.dumps(
                {
                    **self.base_payload,
                    "category_id": str(office.id),
                }
            ),
            content_type="application/json",
        )
        product_id = create_response.json()["id"]

        response = self.client.post(
            f"/categories/{self.category.id}/products/",
            data=json.dumps({"product_id": product_id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"]["id"], str(self.category.id))

    def test_can_remove_product_from_category_to_uncategorized(self):
        create_response = self.client.post(
            "/products/",
            data=json.dumps(self.base_payload),
            content_type="application/json",
        )
        product_id = create_response.json()["id"]

        response = self.client.delete(
            f"/categories/{self.category.id}/products/{product_id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"]["title"], "Uncategorized")

    def test_bulk_csv_import(self):
        csv_body = (
            "name,description,category_id,price,brand,quantity\n"
            f"Mouse,Wireless,{self.category.id},24.99,Logi,8\n"
            f"Monitor,27 inch,{self.category.id},199.99,ViewEdge,5\n"
        )

        response = self.client.post(
            "/products/bulk/",
            data=csv_body,
            content_type="text/csv",
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["created_count"], 2)
        self.assertEqual(len(body["products"]), 2)

    def test_bulk_csv_page_renders_for_browser(self):
        response = self.client.get("/products/bulk/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bulk Product Import")
        self.assertContains(response, "Upload CSV")

    def test_bulk_csv_import_accepts_uploaded_file(self):
        csv_body = (
            "name,description,category_id,price,brand,quantity\n"
            f"Mouse,Wireless,{self.category.id},24.99,Logi,8\n"
        )
        csv_file = SimpleUploadedFile(
            "products.csv",
            csv_body.encode("utf-8"),
            content_type="text/csv",
        )

        response = self.client.post("/products/bulk/", data={"file": csv_file})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["created_count"], 1)

    def test_bulk_csv_import_reports_row_errors(self):
        csv_body = (
            "name,description,category_id,price,brand,quantity\n"
            f"Mouse,Wireless,{self.category.id},24.99,,8\n"
        )

        response = self.client.post(
            "/products/bulk/",
            data=csv_body,
            content_type="text/csv",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "Bulk import failed.")
        self.assertEqual(response.json()["rows"][0]["row"], 2)

    def test_normalize_missing_brands(self):
        Product(
            name="Legacy Laptop",
            description="Old record",
            category=self.category,
            price=899.99,
            brand="",
            quantity=2,
        ).save(validate=False)

        response = self.client.post(
            "/products/normalize-brands/",
            data=json.dumps({"default_brand": "Backfilled Brand"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["updated_count"], 1)
        self.assertEqual(response.json()["products"][0]["brand"], "Backfilled Brand")

    def test_update_requires_brand_for_legacy_product_without_brand(self):
        legacy_product = Product(
            name="Legacy Laptop",
            description="Old record",
            category=self.category,
            price=899.99,
            brand="",
            quantity=2,
        ).save(validate=False)

        response = self.client.put(
            f"/products/{legacy_product.id}/",
            data=json.dumps({"quantity": 3}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "error": "Existing product is missing a brand. Provide 'brand' or run the brand normalization endpoint."
            },
        )

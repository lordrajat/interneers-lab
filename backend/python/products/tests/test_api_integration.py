import json

from products.tests.integration_setup import MongoIntegrationTestCase
from products.tests.seed_data import seed_categories, seed_products


class ProductApiIntegrationTests(MongoIntegrationTestCase):
    def test_end_to_end_products_and_categories_flow(self):
        seeds = seed_categories()
        seed_products(seeds)

        create_category_response = self.client.post(
            "/categories/",
            data=json.dumps(
                {
                    "title": "Kitchen",
                    "description": "Kitchen essentials",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(create_category_response.status_code, 201)
        kitchen_id = create_category_response.json()["id"]

        list_categories_response = self.client.get("/categories/")
        self.assertEqual(list_categories_response.status_code, 200)
        self.assertGreaterEqual(len(list_categories_response.json()["categories"]), 3)

        create_product_response = self.client.post(
            "/products/",
            data=json.dumps(
                {
                    "name": "Mixer",
                    "description": "500W",
                    "category_id": kitchen_id,
                    "price": 149.99,
                    "brand": "BlendX",
                    "quantity": 7,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(create_product_response.status_code, 201)
        product_id = create_product_response.json()["id"]

        get_product_response = self.client.get(f"/products/{product_id}/")
        self.assertEqual(get_product_response.status_code, 200)
        self.assertEqual(get_product_response.json()["name"], "Mixer")
        self.assertEqual(get_product_response.json()["category"]["id"], kitchen_id)

        update_product_response = self.client.put(
            f"/products/{product_id}/",
            data=json.dumps({"quantity": 10, "price": 139.99}),
            content_type="application/json",
        )
        self.assertEqual(update_product_response.status_code, 200)
        self.assertEqual(update_product_response.json()["quantity"], 10)

        kitchen_details_response = self.client.get(f"/categories/{kitchen_id}/")
        self.assertEqual(kitchen_details_response.status_code, 200)
        self.assertEqual(kitchen_details_response.json()["product_count"], 1)
        self.assertEqual(kitchen_details_response.json()["products"][0]["id"], product_id)

        move_response = self.client.post(
            f"/categories/{seeds['electronics'].id}/products/",
            data=json.dumps({"product_id": product_id}),
            content_type="application/json",
        )
        self.assertEqual(move_response.status_code, 200)
        self.assertEqual(
            move_response.json()["category"]["id"],
            str(seeds["electronics"].id),
        )

        remove_response = self.client.delete(
            f"/categories/{seeds['electronics'].id}/products/{product_id}/"
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertEqual(remove_response.json()["category"]["title"], "Uncategorized")

        normalize_response = self.client.post(
            "/products/normalize-brands/",
            data=json.dumps({"default_brand": "Normalized Brand"}),
            content_type="application/json",
        )
        self.assertEqual(normalize_response.status_code, 200)
        self.assertIn("updated_count", normalize_response.json())

        delete_product_response = self.client.delete(f"/products/{product_id}/")
        self.assertEqual(delete_product_response.status_code, 204)

        delete_kitchen_response = self.client.delete(f"/categories/{kitchen_id}/")
        self.assertEqual(delete_kitchen_response.status_code, 204)

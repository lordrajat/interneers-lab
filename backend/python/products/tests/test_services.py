from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from bson import ObjectId

from products.domain.errors import ProductError
from products.services.categories import CategoryService
from products.services.products import ProductService


class ProductServiceTests(TestCase):
    def setUp(self):
        self.product_repository = MagicMock()
        self.category_repository = MagicMock()
        self.service = ProductService(
            repository=self.product_repository,
            category_repository=self.category_repository,
        )

    @patch("products.services.products.serialize_product")
    def test_list_products_serializes_repository_results(self, serialize_product):
        p1 = SimpleNamespace(id="p1")
        p2 = SimpleNamespace(id="p2")
        self.product_repository.list_all.return_value = [p1, p2]
        serialize_product.side_effect = [{"id": "p1"}, {"id": "p2"}]

        result = self.service.list_products()

        self.assertEqual(result, {"products": [{"id": "p1"}, {"id": "p2"}]})
        self.product_repository.list_all.assert_called_once_with()
        serialize_product.assert_has_calls([call(p1), call(p2)])

    def test_get_product_raises_not_found(self):
        self.product_repository.get_by_id.return_value = None

        with self.assertRaises(ProductError) as ctx:
            self.service.get_product(str(ObjectId()))

        self.assertEqual(ctx.exception.message, "Product not found.")
        self.assertEqual(ctx.exception.status, 404)

    def test_update_product_requires_non_empty_partial_payload(self):
        product_id = str(ObjectId())
        self.product_repository.get_by_id.return_value = SimpleNamespace(brand="Lenovo")

        with self.assertRaises(ProductError) as ctx:
            self.service.update_product(product_id, {})

        self.assertEqual(
            ctx.exception.message,
            "At least one valid field is required for update.",
        )
        self.assertEqual(ctx.exception.status, 400)
        self.product_repository.update.assert_not_called()

    def test_update_product_requires_brand_for_legacy_products(self):
        category_id = str(ObjectId())
        product_id = str(ObjectId())
        category = SimpleNamespace(id=ObjectId())
        self.category_repository.get_by_id.return_value = category
        self.product_repository.get_by_id.return_value = SimpleNamespace(brand="")

        with self.assertRaises(ProductError) as ctx:
            self.service.update_product(
                product_id,
                {"category_id": category_id, "quantity": 2},
            )

        self.assertEqual(
            ctx.exception.message,
            "Existing product is missing a brand. Provide 'brand' or run the brand normalization endpoint.",
        )
        self.assertEqual(ctx.exception.status, 400)
        self.product_repository.update.assert_not_called()

    @patch("products.services.products.serialize_product")
    def test_add_product_to_category_updates_category_and_saves(self, serialize_product):
        category_id = str(ObjectId())
        product_id = str(ObjectId())
        category = SimpleNamespace(id=ObjectId())
        product = SimpleNamespace(id=ObjectId(), category=SimpleNamespace(id=ObjectId()))
        self.category_repository.get_by_id.return_value = category
        self.product_repository.get_by_id.return_value = product
        self.product_repository.save.return_value = product
        serialize_product.return_value = {"id": "serialized"}

        result = self.service.add_product_to_category(category_id, {"product_id": product_id})

        self.assertEqual(result, {"id": "serialized"})
        self.assertIs(product.category, category)
        self.product_repository.save.assert_called_once_with(product)

    @patch("products.services.products.serialize_product")
    def test_remove_product_from_category_moves_to_uncategorized(self, serialize_product):
        category_id = str(ObjectId())
        product_id = str(ObjectId())
        category = SimpleNamespace(id=ObjectId(category_id))
        uncategorized = SimpleNamespace(id=ObjectId())
        product = SimpleNamespace(id=ObjectId(product_id), category=SimpleNamespace(id=ObjectId(category_id)))
        self.category_repository.get_by_id.return_value = category
        self.category_repository.get_or_create.return_value = (uncategorized, True)
        self.product_repository.get_by_id.return_value = product
        self.product_repository.save.return_value = product
        serialize_product.return_value = {"category": {"title": "Uncategorized"}}

        result = self.service.remove_product_from_category(category_id, product_id)

        self.assertEqual(result, {"category": {"title": "Uncategorized"}})
        self.assertIs(product.category, uncategorized)
        self.category_repository.get_or_create.assert_called_once()
        self.product_repository.save.assert_called_once_with(product)

    @patch("products.services.products.serialize_product")
    def test_normalize_missing_brands_updates_all_missing(self, serialize_product):
        p1 = SimpleNamespace(brand="")
        p2 = SimpleNamespace(brand=None)
        self.product_repository.list_missing_brand.return_value = [p1, p2]
        self.product_repository.save.side_effect = [p1, p2]
        serialize_product.side_effect = [{"id": "1", "brand": "Backfilled"}, {"id": "2", "brand": "Backfilled"}]

        result = self.service.normalize_missing_brands("  Backfilled  ")

        self.assertEqual(result["updated_count"], 2)
        self.assertEqual(
            result["products"],
            [{"id": "1", "brand": "Backfilled"}, {"id": "2", "brand": "Backfilled"}],
        )
        self.assertEqual(p1.brand, "Backfilled")
        self.assertEqual(p2.brand, "Backfilled")
        self.product_repository.save.assert_has_calls([call(p1), call(p2)])


class CategoryServiceTests(TestCase):
    def setUp(self):
        self.category_repository = MagicMock()
        self.product_repository = MagicMock()
        self.service = CategoryService(
            repository=self.category_repository,
            product_repository=self.product_repository,
        )

    @patch("products.services.categories.serialize_category")
    def test_list_categories_serializes_repository_results(self, serialize_category):
        c1 = SimpleNamespace(id="c1")
        c2 = SimpleNamespace(id="c2")
        self.category_repository.list_all.return_value = [c1, c2]
        serialize_category.side_effect = [{"id": "c1"}, {"id": "c2"}]

        result = self.service.list_categories()

        self.assertEqual(result, {"categories": [{"id": "c1"}, {"id": "c2"}]})
        self.category_repository.list_all.assert_called_once_with()
        serialize_category.assert_has_calls([call(c1), call(c2)])

    @patch("products.services.categories.serialize_product")
    @patch("products.services.categories.serialize_category")
    def test_get_category_includes_products_and_count(
        self,
        serialize_category,
        serialize_product,
    ):
        category_id = str(ObjectId())
        category = SimpleNamespace(id=ObjectId(category_id))
        p1 = SimpleNamespace(id="p1")
        p2 = SimpleNamespace(id="p2")
        self.category_repository.get_by_id.return_value = category
        self.product_repository.list_by_category.return_value = [p1, p2]
        serialize_category.return_value = {"id": category_id, "title": "Electronics"}
        serialize_product.side_effect = [{"id": "p1"}, {"id": "p2"}]

        result = self.service.get_category(category_id)

        self.assertEqual(result["id"], category_id)
        self.assertEqual(result["products"], [{"id": "p1"}, {"id": "p2"}])
        self.assertEqual(result["product_count"], 2)
        self.product_repository.list_by_category.assert_called_once_with(category)

    def test_update_category_rejects_empty_patch(self):
        with self.assertRaises(ProductError) as ctx:
            self.service.update_category(str(ObjectId()), {})

        self.assertEqual(
            ctx.exception.message,
            "At least one valid field is required for update.",
        )
        self.assertEqual(ctx.exception.status, 400)
        self.category_repository.update.assert_not_called()

    def test_delete_category_raises_when_products_exist(self):
        category_id = str(ObjectId())
        category = SimpleNamespace(id=ObjectId(category_id))
        self.category_repository.get_by_id.return_value = category
        self.product_repository.exists_for_category.return_value = True

        with self.assertRaises(ProductError) as ctx:
            self.service.delete_category(category_id)

        self.assertEqual(
            ctx.exception.message,
            "Cannot delete category while products still belong to it.",
        )
        self.assertEqual(ctx.exception.status, 400)
        self.category_repository.delete.assert_not_called()

    def test_delete_category_deletes_when_no_products_exist(self):
        category_id = str(ObjectId())
        category = SimpleNamespace(id=ObjectId(category_id))
        self.category_repository.get_by_id.return_value = category
        self.product_repository.exists_for_category.return_value = False

        self.service.delete_category(category_id)

        self.category_repository.delete.assert_called_once_with(category_id)

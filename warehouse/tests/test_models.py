"""Model validation, DB constraints and model-level behaviour."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase

from warehouse.models import Box, Order, OrderItem, Product
from warehouse.services.box_recommendation import RecommendationInputError, RecommendationStatus

from .helpers import make_box, make_order, make_product

D = Decimal


class ProductModelTests(TestCase):
    def valid_kwargs(self, **overrides):
        data = {
            "name": "Ceramic Mug", "sku": "MUG-001", "length": D("12"), "width": D("9"),
            "height": D("9"), "weight": D("0.4"),
        }
        data.update(overrides)
        return data

    def test_valid_product_passes_full_clean(self):
        Product(**self.valid_kwargs()).full_clean()

    def test_non_positive_dimensions_and_weight_fail_validation(self):
        for field in ("length", "width", "height", "weight"):
            for bad in (D("0"), D("-1")):
                with self.subTest(field=field, value=bad):
                    product = Product(**self.valid_kwargs(**{field: bad}))
                    with self.assertRaises(ValidationError) as ctx:
                        product.full_clean()
                    self.assertIn(field, ctx.exception.message_dict)

    def test_sku_must_be_unique(self):
        make_product(sku="DUP-1")
        with self.assertRaises(ValidationError) as ctx:
            Product(**self.valid_kwargs(sku="DUP-1")).full_clean()
        self.assertIn("sku", ctx.exception.message_dict)

    def test_database_rejects_invalid_row_even_without_full_clean(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(**self.valid_kwargs(length=D("0")))
        with self.assertRaises(IntegrityError), transaction.atomic():
            Product.objects.create(**self.valid_kwargs(weight=D("-2")))

    def test_str_and_absolute_url(self):
        product = make_product(name="Mug", sku="M-1")
        self.assertEqual(str(product), "Mug (M-1)")
        self.assertEqual(product.get_absolute_url(), f"/products/{product.pk}/")

    def test_to_spec_carries_quantity(self):
        spec = make_product(weight="0.4").to_spec(quantity=3)
        self.assertEqual(spec.quantity, 3)
        self.assertEqual(spec.total_weight, D("1.2"))


class BoxModelTests(TestCase):
    def valid_kwargs(self, **overrides):
        data = {
            "name": "Small", "length": D("20"), "width": D("15"), "height": D("10"),
            "max_weight": D("5"), "cost": D("1.50"),
        }
        data.update(overrides)
        return data

    def test_valid_box_passes_full_clean(self):
        Box(**self.valid_kwargs()).full_clean()

    def test_zero_cost_is_allowed(self):
        Box(**self.valid_kwargs(cost=D("0"))).full_clean()

    def test_negative_cost_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            Box(**self.valid_kwargs(cost=D("-0.01"))).full_clean()
        self.assertIn("cost", ctx.exception.message_dict)

    def test_non_positive_dimensions_and_capacity_are_rejected(self):
        for field in ("length", "width", "height", "max_weight"):
            with self.subTest(field=field):
                with self.assertRaises(ValidationError) as ctx:
                    Box(**self.valid_kwargs(**{field: D("0")})).full_clean()
                self.assertIn(field, ctx.exception.message_dict)

    def test_cost_uses_decimal_not_float(self):
        box = make_box(cost="0.10")
        box.refresh_from_db()
        self.assertIsInstance(box.cost, Decimal)
        self.assertEqual(box.cost + D("0.20"), D("0.30"))

    def test_database_rejects_negative_cost(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Box.objects.create(**self.valid_kwargs(cost=D("-1")))

    def test_box_name_must_be_unique(self):
        make_box(name="Dup")
        with self.assertRaises(ValidationError):
            Box(**self.valid_kwargs(name="Dup")).full_clean()


class OrderModelTests(TestCase):
    def setUp(self):
        self.mug = make_product("Mug", weight="0.4")
        self.plate = make_product("Plate", length="26", width="26", height="3", weight="0.75")

    def test_quantity_changes_total_weight(self):
        self.assertEqual(make_order((self.mug, 1)).total_weight, D("0.4"))
        self.assertEqual(make_order((self.mug, 5)).total_weight, D("2.0"))

    def test_total_weight_and_units_across_multiple_products(self):
        order = make_order((self.mug, 2), (self.plate, 4))
        self.assertEqual(order.total_weight, D("3.8"))
        self.assertEqual(order.total_units, 6)

    def test_order_item_line_weight(self):
        order = make_order((self.plate, 3))
        self.assertEqual(order.items.get().line_weight, D("2.25"))

    def test_quantity_must_be_at_least_one(self):
        order = Order.objects.create()
        with self.assertRaises(ValidationError) as ctx:
            OrderItem(order=order, product=self.mug, quantity=0).full_clean()
        self.assertIn("quantity", ctx.exception.message_dict)
        with self.assertRaises(IntegrityError), transaction.atomic():
            OrderItem.objects.create(order=order, product=self.mug, quantity=0)

    def test_same_product_cannot_appear_twice_in_one_order(self):
        order = make_order((self.mug, 1))
        with self.assertRaises(IntegrityError), transaction.atomic():
            OrderItem.objects.create(order=order, product=self.mug, quantity=2)

    def test_product_on_an_order_cannot_be_deleted(self):
        make_order((self.mug, 1))
        with self.assertRaises(ProtectedError):
            self.mug.delete()

    def test_deleting_an_order_removes_its_items(self):
        order = make_order((self.mug, 1))
        order.delete()
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertTrue(Product.objects.filter(pk=self.mug.pk).exists())

    def test_str_includes_reference(self):
        self.assertIn("PO-77", str(make_order((self.mug, 1), reference="PO-77")))

    def test_recommend_box_uses_database_boxes_cheapest_first(self):
        make_box("Pricey", cost="9.00")
        make_box("Cheap", cost="1.00")
        result = make_order((self.mug, 2)).recommend_box()
        self.assertEqual(result.recommended.box.name, "Cheap")
        self.assertEqual([e.box.name for e in result.eligible_boxes], ["Cheap", "Pricey"])

    def test_recommend_box_with_no_boxes_configured(self):
        result = make_order((self.mug, 1)).recommend_box()
        self.assertEqual(result.status, RecommendationStatus.NO_BOXES)

    def test_recommend_box_for_empty_order_raises(self):
        make_box()
        with self.assertRaises(RecommendationInputError):
            Order.objects.create().recommend_box()

"""Unit tests for the pure recommendation service (no database needed)."""

from decimal import Decimal
from itertools import permutations

from django.test import SimpleTestCase

from warehouse.services.box_recommendation import (
    PACKING_DISCLAIMER,
    BoxSpec,
    ItemSpec,
    RecommendationInputError,
    RecommendationStatus,
    calculate_total_weight,
    evaluate_box,
    fits_in_box,
    orientations,
    recommend_boxes,
)

from .helpers import make_box_spec, make_item

D = Decimal


class FitsInBoxTests(SimpleTestCase):
    def test_product_fits_in_exact_dimensions(self):
        self.assertTrue(fits_in_box((D(20), D(15), D(10)), (D(20), D(15), D(10))))

    def test_product_does_not_fit_in_one_dimension(self):
        # Two sides match the box exactly; the third is 0.01 too big. No
        # orientation can help because the box's smallest side is 10.
        self.assertFalse(fits_in_box((D(20), D(15), D("10.01")), (D(20), D(15), D(10))))

    def test_rotation_allows_a_valid_fit(self):
        # Long thin item: as listed (30 x 5 x 10) it overflows a 10 x 30 x 5 box
        # on every axis, but rotated it fits.
        self.assertFalse(
            all(i <= b for i, b in zip((D(30), D(5), D(10)), (D(10), D(30), D(5))))
        )
        self.assertTrue(fits_in_box((D(30), D(5), D(10)), (D(10), D(30), D(5))))

    def test_all_six_permutations_are_tested(self):
        dims = (D(1), D(2), D(3))
        self.assertEqual(len(orientations(dims)), 6)
        self.assertEqual(set(orientations(dims)), set(permutations(dims)))

    def test_every_orientation_of_the_item_fits_a_matching_box(self):
        dims = (D(4), D(7), D(11))
        for box_dims in permutations(dims):
            with self.subTest(box=box_dims):
                self.assertTrue(fits_in_box(dims, box_dims))

    def test_item_too_large_in_all_orientations(self):
        self.assertFalse(fits_in_box((D(25), D(25), D(25)), (D(30), D(30), D(20))))


class TotalWeightTests(SimpleTestCase):
    def test_quantity_changes_total_weight(self):
        one = [make_item(weight="0.4", quantity=1)]
        three = [make_item(weight="0.4", quantity=3)]
        self.assertEqual(calculate_total_weight(one), D("0.4"))
        self.assertEqual(calculate_total_weight(three), D("1.2"))

    def test_multiple_products_are_summed(self):
        items = [
            make_item("Mug", weight="0.4", quantity=2),
            make_item("Plate", weight="0.75", quantity=4),
        ]
        self.assertEqual(calculate_total_weight(items), D("3.8"))

    def test_decimal_arithmetic_is_exact(self):
        # 0.1 x 3 is 0.30000000000000004 with floats; Decimal gives exactly 0.3.
        self.assertEqual(calculate_total_weight([make_item(weight="0.1", quantity=3)]), D("0.3"))

    def test_empty_list_weighs_zero(self):
        self.assertEqual(calculate_total_weight([]), D("0"))


class RecommendationTests(SimpleTestCase):
    def test_basic_valid_recommendation(self):
        result = recommend_boxes([make_item()], [make_box_spec(name="Small Box")])
        self.assertEqual(result.status, RecommendationStatus.RECOMMENDED)
        self.assertTrue(result.has_recommendation)
        self.assertEqual(result.recommended.box.name, "Small Box")
        self.assertEqual(result.total_weight, D("0.4"))
        self.assertEqual(result.total_units, 1)

    def test_cheapest_eligible_box_is_selected(self):
        boxes = [
            make_box_spec("Premium", cost="9.00"),
            make_box_spec("Budget", cost="1.25"),
            make_box_spec("Standard", cost="3.00"),
        ]
        result = recommend_boxes([make_item()], boxes)
        self.assertEqual(result.recommended.box.name, "Budget")

    def test_cheapest_box_is_skipped_when_it_is_too_small(self):
        boxes = [
            make_box_spec("Tiny", length="5", width="5", height="5", cost="0.50"),
            make_box_spec("Right size", cost="2.00"),
        ]
        result = recommend_boxes([make_item()], boxes)
        self.assertEqual(result.recommended.box.name, "Right size")
        self.assertEqual([e.box.name for e in result.rejected_boxes], ["Tiny"])

    def test_boxes_are_sorted_by_cost_cheapest_first(self):
        boxes = [
            make_box_spec("C", cost="5.00"),
            make_box_spec("A", cost="1.00"),
            make_box_spec("B", cost="2.50"),
        ]
        result = recommend_boxes([make_item()], boxes)
        self.assertEqual([e.box.name for e in result.eligible_boxes], ["A", "B", "C"])

    def test_equal_cost_ties_prefer_smaller_volume_then_name(self):
        boxes = [
            make_box_spec("Zeta", length="30", cost="2.00"),
            make_box_spec("Beta", length="25", cost="2.00"),
            make_box_spec("Alpha", length="25", cost="2.00"),
        ]
        result = recommend_boxes([make_item()], boxes)
        self.assertEqual([e.box.name for e in result.eligible_boxes], ["Alpha", "Beta", "Zeta"])

    def test_no_eligible_box_returns_explanation_not_a_box(self):
        giant = make_item("Wardrobe", length="200", width="100", height="60", weight="40")
        result = recommend_boxes([giant], [make_box_spec("Small"), make_box_spec("Medium", length="40")])
        self.assertEqual(result.status, RecommendationStatus.NO_ELIGIBLE_BOX)
        self.assertIsNone(result.recommended)
        self.assertFalse(result.has_recommendation)
        self.assertEqual(result.eligible_boxes, ())
        self.assertEqual(len(result.rejected_boxes), 2)
        self.assertIn("No suitable box", result.message)

    def test_weight_exactly_equal_to_capacity_is_allowed(self):
        item = make_item(weight="2.5", quantity=2)  # 5.0 total
        result = recommend_boxes([item], [make_box_spec(max_weight="5")])
        self.assertTrue(result.has_recommendation)

    def test_weight_exceeding_capacity_is_rejected(self):
        item = make_item(weight="2.501", quantity=2)  # 5.002 > 5
        result = recommend_boxes([item], [make_box_spec(max_weight="5")])
        self.assertFalse(result.has_recommendation)
        rejection = result.rejected_boxes[0].rejections[0]
        self.assertEqual(rejection.code, "weight")
        self.assertIn("exceeds", rejection.message)

    def test_quantity_can_push_an_order_over_capacity(self):
        box = make_box_spec(max_weight="1.0", length="100", width="100", height="100")
        self.assertTrue(recommend_boxes([make_item(weight="0.4", quantity=2)], [box]).has_recommendation)
        self.assertFalse(recommend_boxes([make_item(weight="0.4", quantity=3)], [box]).has_recommendation)

    def test_exact_decimal_weight_match_is_not_broken_by_float_error(self):
        item = make_item(weight="0.1", quantity=3)
        result = recommend_boxes([item], [make_box_spec(max_weight="0.3")])
        self.assertTrue(result.has_recommendation)

    def test_every_product_in_a_multi_product_order_is_checked(self):
        mug = make_item("Mug", length="10", width="10", height="10", weight="0.3")
        poster_tube = make_item("Poster tube", length="60", width="8", height="8", weight="0.5")
        boxes = [
            make_box_spec("Cube", length="30", width="30", height="30", cost="1.00"),
            make_box_spec("Long", length="65", width="20", height="20", cost="4.00"),
        ]
        result = recommend_boxes([mug, poster_tube], boxes)
        # The cheap cube holds the mug but not the 60 cm tube.
        self.assertEqual(result.recommended.box.name, "Long")
        cube = result.rejected_boxes[0]
        self.assertEqual(cube.box.name, "Cube")
        self.assertIn("Poster tube", cube.rejections[0].message)

    def test_multi_product_weights_are_combined_against_capacity(self):
        items = [make_item("A", weight="2"), make_item("B", weight="2"), make_item("C", weight="2")]
        box = make_box_spec(max_weight="5", length="100", width="100", height="100")
        result = recommend_boxes(items, [box])  # 6 kg > 5 kg even though each item is fine
        self.assertFalse(result.has_recommendation)
        self.assertEqual(result.total_weight, D("6"))

    def test_all_failure_reasons_are_reported(self):
        item = make_item("Anvil", length="50", width="50", height="50", weight="90")
        result = recommend_boxes([item], [make_box_spec()])
        codes = {r.code for r in result.rejected_boxes[0].rejections}
        self.assertEqual(codes, {"dimensions", "weight", "volume"})

    def test_volume_check_rejects_boxes_that_can_never_hold_the_order(self):
        cube = make_item("Cube", length="6", width="6", height="6", weight="0.1", quantity=3)  # 648
        box = make_box_spec(length="10", width="10", height="6", max_weight="50")  # volume 600
        evaluation = evaluate_box([cube], box)
        self.assertFalse(evaluation.eligible)
        self.assertEqual([r.code for r in evaluation.rejections], ["volume"])

    def test_known_limitation_passing_checks_is_not_a_packing_guarantee(self):
        """Documents the simplification: two 6-cubes cannot really fit a 10x10x6 box."""
        cube = make_item("Cube", length="6", width="6", height="6", weight="0.1", quantity=2)
        box = make_box_spec(length="10", width="10", height="6", max_weight="50")
        result = recommend_boxes([cube], [box])
        # Volume 432 <= 600 and each cube fits, so the simplified check passes
        # even though two 6 cm cubes need 12 cm along some axis. The UI shows a
        # disclaimer for exactly this reason.
        self.assertTrue(result.has_recommendation)
        self.assertEqual(result.disclaimer, PACKING_DISCLAIMER)
        self.assertIn("does not perform full 3D packing", result.disclaimer)

    def test_result_always_carries_the_disclaimer(self):
        result = recommend_boxes([make_item()], [make_box_spec()])
        self.assertIn("cannot guarantee", result.disclaimer)

    def test_no_boxes_configured(self):
        for boxes in ([], None):
            with self.subTest(boxes=boxes):
                result = recommend_boxes([make_item()], boxes)
                self.assertEqual(result.status, RecommendationStatus.NO_BOXES)
                self.assertIsNone(result.recommended)
                self.assertIn("No shipping boxes are configured", result.message)
                self.assertEqual(result.total_weight, D("0.4"))


class InvalidInputTests(SimpleTestCase):
    def test_empty_order_is_rejected(self):
        with self.assertRaisesMessage(RecommendationInputError, "order is empty"):
            recommend_boxes([], [make_box_spec()])

    def test_missing_order_is_rejected(self):
        with self.assertRaises(RecommendationInputError):
            recommend_boxes(None, [make_box_spec()])

    def test_missing_product_entry_is_rejected(self):
        with self.assertRaisesMessage(RecommendationInputError, "Order item #2"):
            recommend_boxes([make_item(), None], [make_box_spec()])

    def test_missing_box_entry_is_rejected(self):
        with self.assertRaisesMessage(RecommendationInputError, "Box #1"):
            recommend_boxes([make_item()], [None])

    def test_invalid_product_dimensions_and_weight(self):
        bad_values = ["0", "-1", "-0.01", None, "abc", "", "NaN", "Infinity", True]
        for field in ("length", "width", "height", "weight"):
            for bad in bad_values:
                with self.subTest(field=field, value=bad):
                    kwargs = {
                        "name": "Mug", "length": D(10), "width": D(10), "height": D(10),
                        "weight": D(1), "quantity": 1,
                    }
                    kwargs[field] = bad
                    with self.assertRaises(RecommendationInputError):
                        ItemSpec(**kwargs)

    def test_invalid_quantities(self):
        for bad in (0, -1, -10, 1.5, "2", None, True):
            with self.subTest(quantity=bad):
                with self.assertRaises(RecommendationInputError):
                    make_item(quantity=bad)

    def test_product_name_is_required(self):
        with self.assertRaises(RecommendationInputError):
            make_item(name="   ")

    def test_invalid_box_values(self):
        for field, bad in [
            ("length", "0"), ("width", "-5"), ("height", None), ("max_weight", "0"),
            ("max_weight", "-1"), ("cost", "-0.01"), ("cost", "free"),
        ]:
            with self.subTest(field=field, value=bad):
                kwargs = {
                    "name": "Box", "length": D(10), "width": D(10), "height": D(10),
                    "max_weight": D(5), "cost": D(1),
                }
                kwargs[field] = bad
                with self.assertRaises(RecommendationInputError):
                    BoxSpec(**kwargs)

    def test_zero_cost_box_is_valid(self):
        self.assertEqual(make_box_spec(cost="0").cost, D("0"))

    def test_numeric_strings_and_floats_are_coerced_to_decimal(self):
        item = ItemSpec("Mug", "10", 8.5, D("7"), "0.25", 2)
        self.assertEqual(item.width, D("8.5"))
        self.assertIsInstance(item.length, Decimal)
        self.assertEqual(item.total_weight, D("0.50"))

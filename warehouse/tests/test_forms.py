"""Form and formset validation."""

from django.test import TestCase

from warehouse.forms import BoxForm, OrderItemFormSet, ProductForm
from warehouse.models import Order

from .helpers import make_box, make_product


def product_data(**overrides):
    data = {
        "name": "Ceramic Mug", "sku": "mug-001", "length": "12", "width": "9",
        "height": "9", "weight": "0.4",
    }
    data.update(overrides)
    return data


def box_data(**overrides):
    data = {
        "name": "Small", "length": "20", "width": "15", "height": "10",
        "max_weight": "5", "cost": "1.50",
    }
    data.update(overrides)
    return data


class ProductFormTests(TestCase):
    def test_valid_form_and_sku_normalisation(self):
        form = ProductForm(product_data(sku="  mug-001 "))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["sku"], "MUG-001")

    def test_sku_uniqueness_is_case_insensitive_via_normalisation(self):
        make_product(sku="MUG-001")
        form = ProductForm(product_data(sku="mug-001"))
        self.assertFalse(form.is_valid())
        self.assertIn("sku", form.errors)

    def test_non_positive_values_give_helpful_errors(self):
        for field in ("length", "width", "height", "weight"):
            for bad in ("0", "-3"):
                with self.subTest(field=field, value=bad):
                    form = ProductForm(product_data(**{field: bad}))
                    self.assertFalse(form.is_valid())
                    self.assertIn("greater than zero", form.errors[field][0])

    def test_non_numeric_and_missing_values(self):
        form = ProductForm(product_data(length="abc", weight=""))
        self.assertFalse(form.is_valid())
        self.assertIn("length", form.errors)
        self.assertIn("weight", form.errors)

    def test_required_fields(self):
        form = ProductForm({})
        self.assertFalse(form.is_valid())
        for field in ("name", "sku", "length", "width", "height", "weight"):
            self.assertIn(field, form.errors)


class BoxFormTests(TestCase):
    def test_valid_form(self):
        self.assertTrue(BoxForm(box_data()).is_valid())

    def test_zero_cost_is_valid(self):
        self.assertTrue(BoxForm(box_data(cost="0")).is_valid())

    def test_negative_cost_is_invalid(self):
        form = BoxForm(box_data(cost="-1"))
        self.assertFalse(form.is_valid())
        self.assertIn("cannot be negative", form.errors["cost"][0])

    def test_non_positive_dimensions_and_capacity(self):
        for field in ("length", "width", "height", "max_weight"):
            with self.subTest(field=field):
                form = BoxForm(box_data(**{field: "0"}))
                self.assertFalse(form.is_valid())
                self.assertIn(field, form.errors)

    def test_duplicate_name_rejected(self):
        make_box(name="Small")
        self.assertFalse(BoxForm(box_data(name="Small")).is_valid())


class OrderItemFormSetTests(TestCase):
    def setUp(self):
        self.mug = make_product("Mug")
        self.plate = make_product("Plate", weight="0.75")

    def formset(self, rows):
        """Build a bound formset from ``[(product_id, quantity), ...]``."""
        prefix = OrderItemFormSet.get_default_prefix()
        data = {
            f"{prefix}-TOTAL_FORMS": str(len(rows)),
            f"{prefix}-INITIAL_FORMS": "0",
            f"{prefix}-MIN_NUM_FORMS": "1",
            f"{prefix}-MAX_NUM_FORMS": "1000",
        }
        for index, (product_id, quantity) in enumerate(rows):
            data[f"{prefix}-{index}-product"] = str(product_id)
            data[f"{prefix}-{index}-quantity"] = str(quantity)
        return OrderItemFormSet(data, instance=Order())

    def test_valid_formset(self):
        self.assertTrue(self.formset([(self.mug.pk, 2), (self.plate.pk, 1)]).is_valid())

    def test_untouched_extra_rows_are_ignored(self):
        # A browser submits blank rows with the default quantity of 1 untouched.
        self.assertTrue(self.formset([(self.mug.pk, 2), ("", "1")]).is_valid())

    def test_quantity_input_has_min_1_in_html(self):
        formset = OrderItemFormSet(instance=Order())
        self.assertIn('min="1"', str(formset.forms[0]["quantity"]))

    def test_at_least_one_item_is_required(self):
        formset = self.formset([("", "")])
        self.assertFalse(formset.is_valid())

    def test_invalid_quantities_are_rejected(self):
        for bad in ("0", "-2", "1.5", "abc"):
            with self.subTest(quantity=bad):
                formset = self.formset([(self.mug.pk, bad)])
                self.assertFalse(formset.is_valid())
                self.assertIn("quantity", formset.errors[0])

    def test_unknown_product_is_rejected(self):
        formset = self.formset([(99999, 1)])
        self.assertFalse(formset.is_valid())
        self.assertIn("product", formset.errors[0])

    def test_duplicate_products_are_rejected_with_clear_message(self):
        formset = self.formset([(self.mug.pk, 1), (self.mug.pk, 2)])
        self.assertFalse(formset.is_valid())
        self.assertIn("listed more than once", " ".join(formset.non_form_errors()))

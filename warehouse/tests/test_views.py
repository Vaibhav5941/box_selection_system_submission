"""HTTP-level tests for the main user flows."""

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from warehouse.models import Box, Order, OrderItem, Product
from warehouse.services.box_recommendation import PACKING_DISCLAIMER

from .helpers import make_box, make_order, make_product
from .test_forms import box_data, product_data


def message_texts(response):
    return [str(message) for message in get_messages(response.wsgi_request)]


class DashboardViewTests(TestCase):
    def test_empty_state(self):
        response = self.client.get(reverse("warehouse:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Getting started")
        self.assertContains(response, "No orders yet")

    def test_shows_counts_and_recent_orders(self):
        make_box()
        order = make_order((make_product(), 2))
        response = self.client.get(reverse("warehouse:dashboard"))
        self.assertContains(response, str(order))
        self.assertEqual(response.context["box_count"], 1)
        self.assertEqual(response.context["order_count"], 1)

    def test_navigation_links_present(self):
        response = self.client.get(reverse("warehouse:dashboard"))
        for name in ("product_list", "box_list", "order_list"):
            self.assertContains(response, reverse(f"warehouse:{name}"))


class ProductViewTests(TestCase):
    def test_list_empty_state(self):
        response = self.client.get(reverse("warehouse:product_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No products yet")

    def test_list_shows_products(self):
        make_product("Ceramic Mug", sku="MUG-1")
        response = self.client.get(reverse("warehouse:product_list"))
        self.assertContains(response, "Ceramic Mug")
        self.assertContains(response, "MUG-1")

    def test_create_get_renders_form(self):
        response = self.client.get(reverse("warehouse:product_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_create_post_valid(self):
        response = self.client.post(reverse("warehouse:product_create"), product_data(), follow=True)
        self.assertRedirects(response, reverse("warehouse:product_list"))
        self.assertTrue(Product.objects.filter(sku="MUG-001").exists())
        self.assertContains(response, "was created")

    def test_create_post_invalid_shows_errors_and_saves_nothing(self):
        response = self.client.post(reverse("warehouse:product_create"), product_data(length="-5"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a value greater than zero.")
        self.assertEqual(Product.objects.count(), 0)

    def test_detail_update_and_delete(self):
        product = make_product("Mug", sku="M-1")
        detail = self.client.get(reverse("warehouse:product_detail", args=[product.pk]))
        self.assertContains(detail, "M-1")

        update_url = reverse("warehouse:product_update", args=[product.pk])
        response = self.client.post(update_url, product_data(name="Big Mug", sku="M-1"))
        self.assertRedirects(response, product.get_absolute_url())
        product.refresh_from_db()
        self.assertEqual(product.name, "Big Mug")

        delete_url = reverse("warehouse:product_delete", args=[product.pk])
        self.assertEqual(self.client.get(delete_url).status_code, 200)
        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("warehouse:product_list"))
        self.assertFalse(Product.objects.exists())

    def test_missing_product_returns_404(self):
        for name in ("product_detail", "product_update", "product_delete"):
            with self.subTest(view=name):
                self.assertEqual(self.client.get(reverse(f"warehouse:{name}", args=[999])).status_code, 404)

    def test_product_used_by_an_order_is_not_deleted(self):
        product = make_product()
        make_order((product, 1))
        response = self.client.post(reverse("warehouse:product_delete", args=[product.pk]), follow=True)
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())
        self.assertContains(response, "cannot be deleted")


class BoxViewTests(TestCase):
    def test_list_empty_state(self):
        self.assertContains(self.client.get(reverse("warehouse:box_list")), "No boxes yet")

    def test_create_valid_and_invalid(self):
        url = reverse("warehouse:box_create")
        response = self.client.post(url, box_data(), follow=True)
        self.assertRedirects(response, reverse("warehouse:box_list"))
        self.assertEqual(Box.objects.count(), 1)

        bad = self.client.post(url, box_data(name="Bad", cost="-2"))
        self.assertEqual(bad.status_code, 200)
        self.assertContains(bad, "cannot be negative")
        self.assertEqual(Box.objects.count(), 1)

    def test_detail_update_delete(self):
        box = make_box("Small", cost="1.50")
        self.assertContains(self.client.get(reverse("warehouse:box_detail", args=[box.pk])), "Small")
        response = self.client.post(
            reverse("warehouse:box_update", args=[box.pk]), box_data(name="Small", cost="2.25")
        )
        self.assertRedirects(response, box.get_absolute_url())
        box.refresh_from_db()
        self.assertEqual(str(box.cost), "2.25")
        self.client.post(reverse("warehouse:box_delete", args=[box.pk]))
        self.assertFalse(Box.objects.exists())

    def test_missing_box_returns_404(self):
        self.assertEqual(self.client.get(reverse("warehouse:box_detail", args=[42])).status_code, 404)


class OrderCreateViewTests(TestCase):
    url = reverse("warehouse:order_create")

    def setUp(self):
        self.mug = make_product("Mug", weight="0.4")
        self.plate = make_product("Plate", weight="0.75")

    def post(self, rows, **extra):
        data = {
            "items-TOTAL_FORMS": str(len(rows)), "items-INITIAL_FORMS": "0",
            "items-MIN_NUM_FORMS": "1", "items-MAX_NUM_FORMS": "1000",
            "reference": "PO-100", "notes": "",
        }
        data.update(extra)
        for index, (product_id, quantity) in enumerate(rows):
            data[f"items-{index}-product"] = str(product_id)
            data[f"items-{index}-quantity"] = str(quantity)
        return self.client.post(self.url, data)

    def test_get_without_products_shows_empty_state(self):
        Product.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no products to order yet")

    def test_get_renders_formset(self):
        response = self.client.get(self.url)
        self.assertContains(response, "items-0-product")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_order_is_created_with_items(self):
        response = self.post([(self.mug.pk, 2), (self.plate.pk, 1)])
        order = Order.objects.get()
        self.assertRedirects(response, order.get_absolute_url())
        self.assertEqual(order.items.count(), 2)
        self.assertEqual(str(order.total_weight), "1.550")

    def test_invalid_quantity_creates_nothing(self):
        for bad in ("0", "-1", "1.5", "abc"):
            with self.subTest(quantity=bad):
                response = self.post([(self.mug.pk, bad)])
                self.assertEqual(response.status_code, 200)
                self.assertEqual(Order.objects.count(), 0)
                self.assertEqual(OrderItem.objects.count(), 0)

    def test_empty_order_is_rejected(self):
        response = self.post([("", "")])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.assertContains(response, "Please correct the errors below.")

    def test_duplicate_product_is_rejected(self):
        response = self.post([(self.mug.pk, 1), (self.mug.pk, 1)])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "listed more than once")
        self.assertEqual(Order.objects.count(), 0)


class OrderDetailAndListTests(TestCase):
    def setUp(self):
        self.mug = make_product("Ceramic Mug", sku="MUG-1", weight="0.4")
        self.plate = make_product("Stoneware Plate", sku="PLT-1", weight="0.75")
        self.order = make_order((self.mug, 3), (self.plate, 2), reference="PO-9")

    def test_detail_shows_products_quantities_and_total_weight(self):
        response = self.client.get(self.order.get_absolute_url())
        self.assertContains(response, "Ceramic Mug")
        self.assertContains(response, "Stoneware Plate")
        self.assertContains(response, "MUG-1")
        self.assertEqual(response.context["order"].total_weight, self.mug.weight * 3 + self.plate.weight * 2)
        self.assertContains(response, "2.7")  # 1.2 + 1.5 kg

    def test_list_shows_orders(self):
        response = self.client.get(reverse("warehouse:order_list"))
        self.assertContains(response, "PO-9")

    def test_list_empty_state(self):
        Order.objects.all().delete()
        self.assertContains(self.client.get(reverse("warehouse:order_list")), "No orders yet")

    def test_missing_order_returns_404(self):
        for name in ("order_detail", "order_delete", "order_recommendation"):
            with self.subTest(view=name):
                self.assertEqual(self.client.get(reverse(f"warehouse:{name}", args=[9999])).status_code, 404)

    def test_delete_order(self):
        response = self.client.post(reverse("warehouse:order_delete", args=[self.order.pk]))
        self.assertRedirects(response, reverse("warehouse:order_list"))
        self.assertFalse(Order.objects.exists())
        self.assertTrue(Product.objects.filter(pk=self.mug.pk).exists())


class RecommendationViewTests(TestCase):
    def setUp(self):
        self.mug = make_product("Ceramic Mug", length="12", width="9", height="9", weight="0.4")

    def url(self, order):
        return reverse("warehouse:order_recommendation", args=[order.pk])

    def test_shows_cheapest_eligible_box_and_all_eligible_boxes(self):
        make_box("Premium", cost="9.00")
        make_box("Budget", cost="1.25")
        response = self.client.get(self.url(make_order((self.mug, 2))))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["result"].recommended.box.name, "Budget")
        self.assertContains(response, "Recommended box")
        self.assertContains(response, "Premium")

    def test_always_shows_the_limitation_disclaimer(self):
        make_box()
        response = self.client.get(self.url(make_order((self.mug, 1))))
        self.assertContains(response, "does not perform full 3D packing")
        self.assertContains(response, "cannot guarantee that several products physically fit")
        self.assertIn("cannot guarantee that several products physically fit", PACKING_DISCLAIMER)

    def test_no_eligible_box_shows_clear_explanation(self):
        make_box("Tiny", length="5", width="5", height="5", max_weight="1", cost="0.50")
        response = self.client.get(self.url(make_order((self.mug, 1))))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No suitable box found")
        self.assertContains(response, "does not fit inside")
        self.assertNotContains(response, "Recommended box")

    def test_weight_rejection_is_explained(self):
        make_box("Light", length="50", width="50", height="50", max_weight="0.5", cost="1.00")
        response = self.client.get(self.url(make_order((self.mug, 2))))  # 0.8 kg > 0.5 kg
        self.assertContains(response, "exceeds the box capacity")

    def test_no_boxes_configured_message(self):
        response = self.client.get(self.url(make_order((self.mug, 1))))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No shipping boxes are configured")

    def test_empty_order_is_handled_without_error(self):
        make_box()
        response = self.client.get(self.url(Order.objects.create()))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cannot evaluate this order")
        self.assertContains(response, "order is empty")


class SecurityTests(TestCase):
    def test_post_without_csrf_token_is_forbidden(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("warehouse:product_create"), product_data())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_requires_post(self):
        product = make_product()
        self.client.get(reverse("warehouse:product_delete", args=[product.pk]))
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())

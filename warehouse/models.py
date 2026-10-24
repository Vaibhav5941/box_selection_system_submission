"""Database models: Product, Box, Order and OrderItem.

Units used throughout the UI: dimensions in centimetres, weights in kilograms.
Costs are plain currency amounts (no currency symbol is assumed).

Validation is layered: field validators run in ``full_clean()`` and ModelForms,
while ``CheckConstraint``s make the database itself reject invalid rows even
if someone calls ``Model.objects.create()`` directly.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from .services.box_recommendation import (
    BoxSpec,
    ItemSpec,
    RecommendationResult,
    calculate_total_weight,
    recommend_boxes,
)
from .validators import validate_non_negative, validate_positive

DIMENSION_FIELD = {"max_digits": 8, "decimal_places": 2, "validators": [validate_positive]}
WEIGHT_FIELD = {"max_digits": 10, "decimal_places": 3, "validators": [validate_positive]}


class Product(models.Model):
    """A sellable product with the physical data needed for box selection."""

    name = models.CharField(max_length=120)
    sku = models.CharField("SKU", max_length=40, unique=True)
    length = models.DecimalField("Length (cm)", **DIMENSION_FIELD)
    width = models.DecimalField("Width (cm)", **DIMENSION_FIELD)
    height = models.DecimalField("Height (cm)", **DIMENSION_FIELD)
    weight = models.DecimalField("Weight (kg)", **WEIGHT_FIELD)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.CheckConstraint(condition=models.Q(length__gt=0), name="product_length_positive"),
            models.CheckConstraint(condition=models.Q(width__gt=0), name="product_width_positive"),
            models.CheckConstraint(condition=models.Q(height__gt=0), name="product_height_positive"),
            models.CheckConstraint(condition=models.Q(weight__gt=0), name="product_weight_positive"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.sku})"

    def get_absolute_url(self) -> str:
        return reverse("warehouse:product_detail", args=[self.pk])

    def to_spec(self, quantity: int = 1) -> ItemSpec:
        """Convert to the plain object used by the recommendation service."""
        return ItemSpec(
            name=self.name,
            length=self.length,
            width=self.width,
            height=self.height,
            weight=self.weight,
            quantity=quantity,
        )


class Box(models.Model):
    """A shipping box. Dimensions are INTERNAL (usable) dimensions."""

    name = models.CharField(max_length=120, unique=True)
    length = models.DecimalField("Internal length (cm)", **DIMENSION_FIELD)
    width = models.DecimalField("Internal width (cm)", **DIMENSION_FIELD)
    height = models.DecimalField("Internal height (cm)", **DIMENSION_FIELD)
    max_weight = models.DecimalField("Max weight (kg)", **WEIGHT_FIELD)
    cost = models.DecimalField(
        "Cost", max_digits=10, decimal_places=2, validators=[validate_non_negative]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "boxes"
        ordering = ["cost", "name"]
        constraints = [
            models.CheckConstraint(condition=models.Q(length__gt=0), name="box_length_positive"),
            models.CheckConstraint(condition=models.Q(width__gt=0), name="box_width_positive"),
            models.CheckConstraint(condition=models.Q(height__gt=0), name="box_height_positive"),
            models.CheckConstraint(
                condition=models.Q(max_weight__gt=0), name="box_max_weight_positive"
            ),
            models.CheckConstraint(condition=models.Q(cost__gte=0), name="box_cost_non_negative"),
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("warehouse:box_detail", args=[self.pk])

    def to_spec(self) -> BoxSpec:
        """Convert to the plain object used by the recommendation service."""
        return BoxSpec(
            name=self.name,
            length=self.length,
            width=self.width,
            height=self.height,
            max_weight=self.max_weight,
            cost=self.cost,
            box_id=self.pk,
        )


class Order(models.Model):
    """A customer order made of one or more OrderItems."""

    reference = models.CharField(
        max_length=80, blank=True, help_text="Optional label, e.g. a customer or PO number."
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-pk"]

    def __str__(self) -> str:
        label = f"Order #{self.pk}"
        return f"{label} - {self.reference}" if self.reference else label

    def get_absolute_url(self) -> str:
        return reverse("warehouse:order_detail", args=[self.pk])

    def item_specs(self) -> list[ItemSpec]:
        """All order lines as service objects (use prefetch to avoid N+1)."""
        return [item.to_spec() for item in self.items.all()]

    @property
    def total_units(self) -> int:
        return sum(item.quantity for item in self.items.all())

    @property
    def total_weight(self) -> Decimal:
        """Total weight in kg: sum of unit weight x quantity for every line."""
        return calculate_total_weight(self.item_specs())

    def recommend_box(self, boxes=None) -> RecommendationResult:
        """Run the recommendation engine for this order.

        ``boxes`` defaults to every configured Box. Raises
        ``RecommendationInputError`` for an empty order.
        """
        box_queryset = Box.objects.all() if boxes is None else boxes
        return recommend_boxes(self.item_specs(), [box.to_spec() for box in box_queryset])


class OrderItem(models.Model):
    """One product and quantity within an order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    # PROTECT: a product that appears on an order cannot be deleted by accident.
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(quantity__gte=1), name="orderitem_quantity_min_1"),
            models.UniqueConstraint(fields=["order", "product"], name="orderitem_unique_product_per_order"),
        ]

    def __str__(self) -> str:
        return f"{self.quantity} x {self.product.name}"

    @property
    def line_weight(self) -> Decimal:
        return self.product.weight * self.quantity

    def to_spec(self) -> ItemSpec:
        return self.product.to_spec(quantity=self.quantity)

"""Small factory helpers shared by the test modules (realistic sample data)."""

from decimal import Decimal

from warehouse.models import Box, Order, OrderItem, Product
from warehouse.services.box_recommendation import BoxSpec, ItemSpec

_counter = {"sku": 0, "box": 0}


def make_item(name="Ceramic Mug", length="12", width="9", height="9", weight="0.4", quantity=1):
    """Build an ItemSpec for service-level tests (no database)."""
    return ItemSpec(
        name=name,
        length=Decimal(length),
        width=Decimal(width),
        height=Decimal(height),
        weight=Decimal(weight),
        quantity=quantity,
    )


def make_box_spec(
    name="Small Box", length="20", width="15", height="10", max_weight="5", cost="1.50", box_id=None
):
    """Build a BoxSpec for service-level tests (no database)."""
    return BoxSpec(
        name=name,
        length=Decimal(length),
        width=Decimal(width),
        height=Decimal(height),
        max_weight=Decimal(max_weight),
        cost=Decimal(cost),
        box_id=box_id,
    )


def make_product(name="Ceramic Mug", sku=None, length="12", width="9", height="9", weight="0.4"):
    """Create and save a Product with a unique SKU."""
    if sku is None:
        _counter["sku"] += 1
        sku = f"SKU-{_counter['sku']:04d}"
    return Product.objects.create(
        name=name, sku=sku, length=Decimal(length), width=Decimal(width),
        height=Decimal(height), weight=Decimal(weight),
    )


def make_box(name=None, length="20", width="15", height="10", max_weight="5", cost="1.50"):
    """Create and save a Box with a unique name."""
    if name is None:
        _counter["box"] += 1
        name = f"Box {_counter['box']}"
    return Box.objects.create(
        name=name, length=Decimal(length), width=Decimal(width), height=Decimal(height),
        max_weight=Decimal(max_weight), cost=Decimal(cost),
    )


def make_order(*lines, reference=""):
    """Create an Order from ``(product, quantity)`` pairs."""
    order = Order.objects.create(reference=reference)
    for product, quantity in lines:
        OrderItem.objects.create(order=order, product=product, quantity=quantity)
    return order

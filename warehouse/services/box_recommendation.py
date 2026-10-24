"""
Box recommendation engine.

This module is deliberately free of Django imports so it can be unit-tested
without a database. Models convert themselves into the plain dataclasses
defined here (``ItemSpec`` and ``BoxSpec``) and hand them to
:func:`recommend_boxes`.

Algorithm (simplified selection, NOT a 3D packing solver)
---------------------------------------------------------
A box is *eligible* for an order only if ALL of the following hold:

1. **Per-item fit with rotation.** Every product, considered on its own,
   fits inside the box's internal dimensions in at least one of its six
   axis-aligned orientations (all permutations of length/width/height).
   Exact fits are allowed (``<=``).
2. **Weight capacity.** The total weight of the order
   (``unit weight x quantity`` summed over all items) does not exceed the
   box's maximum supported weight. Exactly equal is allowed.
3. **Volume sanity check.** The combined volume of all units does not exceed
   the box's internal volume. This is a *necessary* condition for any real
   packing, so a box that fails it can never hold the order and is rejected.

Eligible boxes are sorted cheapest first (ties: smaller internal volume, then
name, then id) and the first one is the primary recommendation.

Assumptions and limitations (please read)
-----------------------------------------
* Rules 1-3 are *necessary* conditions, not *sufficient* ones. This module
  does not perform full 3D bin packing, so for orders with several units or
  products it **cannot guarantee** that everything physically fits together
  in the recommended box. Example: two 6 x 6 x 6 cubes pass every check for a
  10 x 10 x 6 box (each cube fits, and 432 <= 600 by volume), yet they cannot
  be packed together because two cubes need 12 units along some axis. Treat
  the result as a shortlist to be confirmed by a person or a real packing
  algorithm.
* Only axis-aligned (90 degree) rotations are considered.
* All dimensions share one unit (cm in the UI) and weights share one unit
  (kg in the UI); no unit conversion is performed.
* Packaging material, fragility, stacking rules and dimensional weight are
  not modelled.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from itertools import permutations
from typing import Iterable, Sequence

# Message shown alongside every recommendation. Kept here so the UI, README and
# tests all reference one honest statement of the limitation.
PACKING_DISCLAIMER = (
    "This is a simplified selection: each product is checked individually "
    "(with rotation), then total weight and total volume are checked against "
    "the box. It does not perform full 3D packing, so it cannot guarantee that "
    "several products physically fit together in the same box."
)


class RecommendationInputError(ValueError):
    """Raised when the order or box data cannot be evaluated safely."""


class RecommendationStatus(StrEnum):
    """Overall outcome of a recommendation request."""

    RECOMMENDED = "recommended"
    NO_BOXES = "no_boxes"
    NO_ELIGIBLE_BOX = "no_eligible_box"


# --------------------------------------------------------------------------
# Input validation helpers
# --------------------------------------------------------------------------


def _to_decimal(value: object, label: str) -> Decimal:
    """Convert ``value`` to a finite Decimal or raise RecommendationInputError."""
    if value is None or isinstance(value, bool):
        raise RecommendationInputError(f"{label} is missing or not a number.")
    if isinstance(value, Decimal):
        number = value
    else:
        try:
            number = Decimal(str(value).strip())
        except InvalidOperation:
            raise RecommendationInputError(
                f"{label} is not a valid number: {value!r}."
            ) from None
    if not number.is_finite():
        raise RecommendationInputError(f"{label} must be a finite number.")
    return number


def _positive_decimal(value: object, label: str) -> Decimal:
    number = _to_decimal(value, label)
    if number <= 0:
        raise RecommendationInputError(f"{label} must be greater than zero.")
    return number


def _clean_name(value: object, label: str) -> str:
    name = "" if value is None else str(value).strip()
    if not name:
        raise RecommendationInputError(f"{label} name is required.")
    return name


# --------------------------------------------------------------------------
# Data classes
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ItemSpec:
    """A product line in an order: one product type and how many units."""

    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    weight: Decimal  # weight of ONE unit
    quantity: int = 1

    def __post_init__(self) -> None:
        name = _clean_name(self.name, "Product")
        object.__setattr__(self, "name", name)
        for field_name in ("length", "width", "height", "weight"):
            value = _positive_decimal(
                getattr(self, field_name), f"Product '{name}': {field_name}"
            )
            object.__setattr__(self, field_name, value)
        quantity = self.quantity
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
            raise RecommendationInputError(
                f"Product '{name}': quantity must be a whole number of at least 1 "
                f"(got {quantity!r})."
            )

    @property
    def dimensions(self) -> tuple[Decimal, Decimal, Decimal]:
        return (self.length, self.width, self.height)

    @property
    def total_weight(self) -> Decimal:
        return self.weight * self.quantity

    @property
    def total_volume(self) -> Decimal:
        return self.length * self.width * self.height * self.quantity


@dataclass(frozen=True)
class BoxSpec:
    """A shipping box, using INTERNAL dimensions."""

    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    max_weight: Decimal
    cost: Decimal
    box_id: int | None = None

    def __post_init__(self) -> None:
        name = _clean_name(self.name, "Box")
        object.__setattr__(self, "name", name)
        for field_name in ("length", "width", "height", "max_weight"):
            value = _positive_decimal(
                getattr(self, field_name), f"Box '{name}': {field_name}"
            )
            object.__setattr__(self, field_name, value)
        cost = _to_decimal(self.cost, f"Box '{name}': cost")
        if cost < 0:
            raise RecommendationInputError(f"Box '{name}': cost cannot be negative.")
        object.__setattr__(self, "cost", cost)

    @property
    def dimensions(self) -> tuple[Decimal, Decimal, Decimal]:
        return (self.length, self.width, self.height)

    @property
    def volume(self) -> Decimal:
        return self.length * self.width * self.height


@dataclass(frozen=True)
class Rejection:
    """One reason a box was rejected. ``code`` is machine readable."""

    code: str  # "dimensions" | "weight" | "volume"
    message: str


@dataclass(frozen=True)
class BoxEvaluation:
    """The outcome of testing a single box against an order."""

    box: BoxSpec
    total_weight: Decimal
    rejections: tuple[Rejection, ...] = field(default_factory=tuple)

    @property
    def eligible(self) -> bool:
        return not self.rejections


@dataclass(frozen=True)
class RecommendationResult:
    """Full result of :func:`recommend_boxes`."""

    status: RecommendationStatus
    message: str
    total_weight: Decimal
    total_units: int
    eligible_boxes: tuple[BoxEvaluation, ...]  # cheapest first
    rejected_boxes: tuple[BoxEvaluation, ...]
    disclaimer: str = PACKING_DISCLAIMER

    @property
    def recommended(self) -> BoxEvaluation | None:
        """The primary recommendation: the cheapest eligible box, if any."""
        return self.eligible_boxes[0] if self.eligible_boxes else None

    @property
    def has_recommendation(self) -> bool:
        return self.recommended is not None


# --------------------------------------------------------------------------
# Core geometry / weight functions
# --------------------------------------------------------------------------


def orientations(
    dimensions: Sequence[Decimal],
) -> list[tuple[Decimal, Decimal, Decimal]]:
    """Return all six permutations of ``(length, width, height)``."""
    return list(permutations(dimensions, 3))


def fits_in_box(
    item_dimensions: Sequence[Decimal], box_dimensions: Sequence[Decimal]
) -> bool:
    """True if the item fits inside the box in at least one orientation.

    An item whose dimension equals the box dimension fits exactly (``<=``).
    """
    return any(
        all(item_side <= box_side for item_side, box_side in zip(orientation, box_dimensions))
        for orientation in orientations(item_dimensions)
    )


def calculate_total_weight(items: Iterable[ItemSpec]) -> Decimal:
    """Sum of ``unit weight x quantity`` over all items (0 for no items)."""
    return sum((item.total_weight for item in items), Decimal("0"))


def calculate_total_volume(items: Iterable[ItemSpec]) -> Decimal:
    """Combined volume of every unit in the order."""
    return sum((item.total_volume for item in items), Decimal("0"))


# --------------------------------------------------------------------------
# Evaluation
# --------------------------------------------------------------------------


def _fmt(number: Decimal) -> str:
    """Format a Decimal without scientific notation or trailing zeros."""
    text = format(number.normalize(), "f")
    return text


def evaluate_box(items: Sequence[ItemSpec], box: BoxSpec) -> BoxEvaluation:
    """Test one box against all items, collecting EVERY reason for rejection."""
    rejections: list[Rejection] = []

    for item in items:
        if not fits_in_box(item.dimensions, box.dimensions):
            l, w, h = (_fmt(side) for side in item.dimensions)
            bl, bw, bh = (_fmt(side) for side in box.dimensions)
            rejections.append(
                Rejection(
                    "dimensions",
                    f"'{item.name}' ({l} x {w} x {h}) does not fit inside "
                    f"{bl} x {bw} x {bh} in any orientation.",
                )
            )

    total_weight = calculate_total_weight(items)
    if total_weight > box.max_weight:
        rejections.append(
            Rejection(
                "weight",
                f"Total weight {_fmt(total_weight)} exceeds the box capacity "
                f"of {_fmt(box.max_weight)}.",
            )
        )

    total_volume = calculate_total_volume(items)
    if total_volume > box.volume:
        rejections.append(
            Rejection(
                "volume",
                f"Combined item volume {_fmt(total_volume)} exceeds the box's "
                f"internal volume {_fmt(box.volume)}.",
            )
        )

    return BoxEvaluation(box=box, total_weight=total_weight, rejections=tuple(rejections))


def _sort_key(evaluation: BoxEvaluation) -> tuple:
    """Cheapest first; deterministic tie-breaks (volume, name, id)."""
    box = evaluation.box
    return (box.cost, box.volume, box.name.lower(), box.box_id or 0)


def _validate_items(items: Iterable[ItemSpec] | None) -> list[ItemSpec]:
    if items is None:
        raise RecommendationInputError("The order has no items to evaluate.")
    item_list = list(items)
    if not item_list:
        raise RecommendationInputError(
            "The order is empty. Add at least one product before requesting a recommendation."
        )
    for position, item in enumerate(item_list, start=1):
        if not isinstance(item, ItemSpec):
            raise RecommendationInputError(
                f"Order item #{position} is missing or invalid (no product data)."
            )
    return item_list


def _validate_boxes(boxes: Iterable[BoxSpec] | None) -> list[BoxSpec]:
    if boxes is None:
        return []
    box_list = list(boxes)
    for position, box in enumerate(box_list, start=1):
        if not isinstance(box, BoxSpec):
            raise RecommendationInputError(f"Box #{position} is missing or invalid.")
    return box_list


def recommend_boxes(
    items: Iterable[ItemSpec] | None, boxes: Iterable[BoxSpec] | None
) -> RecommendationResult:
    """Evaluate every box and recommend the cheapest eligible one.

    Raises:
        RecommendationInputError: if the order is empty or contains an
            invalid entry. (Invalid product/box *values* are rejected earlier,
            when the ``ItemSpec`` / ``BoxSpec`` is constructed.)

    Never silently picks an invalid box: when nothing qualifies the result has
    ``recommended is None`` and a message explaining why.
    """
    item_list = _validate_items(items)
    box_list = _validate_boxes(boxes)

    total_weight = calculate_total_weight(item_list)
    total_units = sum(item.quantity for item in item_list)

    if not box_list:
        return RecommendationResult(
            status=RecommendationStatus.NO_BOXES,
            message=(
                "No shipping boxes are configured. Add at least one box "
                "before requesting a recommendation."
            ),
            total_weight=total_weight,
            total_units=total_units,
            eligible_boxes=(),
            rejected_boxes=(),
        )

    evaluations = [evaluate_box(item_list, box) for box in box_list]
    eligible = sorted((e for e in evaluations if e.eligible), key=_sort_key)
    rejected = sorted((e for e in evaluations if not e.eligible), key=_sort_key)

    if eligible:
        best = eligible[0]
        message = (
            f"Recommended box: {best.box.name} (cost {_fmt(best.box.cost)}), "
            f"the cheapest of {len(eligible)} box(es) passing the simplified checks."
        )
        status = RecommendationStatus.RECOMMENDED
    else:
        message = (
            f"No suitable box found. None of the {len(box_list)} configured box(es) "
            f"can hold this order (total weight {_fmt(total_weight)}). See the "
            f"reasons below, then add a larger or higher-capacity box or split the "
            f"order into several shipments."
        )
        status = RecommendationStatus.NO_ELIGIBLE_BOX

    return RecommendationResult(
        status=status,
        message=message,
        total_weight=total_weight,
        total_units=total_units,
        eligible_boxes=tuple(eligible),
        rejected_boxes=tuple(rejected),
    )

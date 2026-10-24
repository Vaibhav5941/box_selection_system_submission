"""Reusable field validators."""

from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_positive(value: Decimal) -> None:
    """Reject zero and negative numbers (used for dimensions, weights, capacity)."""
    if value is not None and value <= 0:
        raise ValidationError("Enter a value greater than zero.", code="not_positive")


def validate_non_negative(value: Decimal) -> None:
    """Reject negative numbers (used for cost; free boxes are allowed)."""
    if value is not None and value < 0:
        raise ValidationError("Value cannot be negative.", code="negative")

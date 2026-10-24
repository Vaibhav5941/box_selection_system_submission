"""ModelForms and the inline formset used to build an order."""

from django import forms
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Box, Order, OrderItem, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "length", "width", "height", "weight"]

    def clean_name(self):
        return self.cleaned_data["name"].strip()

    def clean_sku(self):
        """Normalise SKUs so 'ab-1' and 'AB-1' cannot both exist."""
        return self.cleaned_data["sku"].strip().upper()


class BoxForm(forms.ModelForm):
    class Meta:
        model = Box
        fields = ["name", "length", "width", "height", "max_weight", "cost"]

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["reference", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 3})}


class OrderItemForm(forms.ModelForm):
    """One order line. Quantity must be a whole number >= 1 (HTML min=1 too)."""

    quantity = forms.IntegerField(min_value=1, initial=1, label="Quantity")

    class Meta:
        model = OrderItem
        fields = ["product", "quantity"]


class BaseOrderItemFormSet(BaseInlineFormSet):
    """Adds a friendly duplicate-product check on top of the standard rules."""

    def clean(self):
        if any(self.errors):
            return  # field-level errors take priority
        # Run before the generic unique check so users get a clearer message
        # than "Please correct the duplicate data for product."
        seen = set()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get("DELETE"):
                continue
            product = form.cleaned_data.get("product")
            if product is None:
                continue
            if product.pk in seen:
                raise forms.ValidationError(
                    f"'{product.name}' is listed more than once. "
                    "Combine duplicates into a single line with the total quantity."
                )
            seen.add(product.pk)
        super().clean()


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    formset=BaseOrderItemFormSet,
    fields=["product", "quantity"],
    extra=3,
    min_num=1,
    validate_min=True,
    can_delete=False,
)

"""Views for the warehouse app.

CRUD for products and boxes uses Django's generic class-based views; the order
workflow uses small purpose-built views because it combines a form and a
formset.
"""

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import BoxForm, OrderForm, OrderItemFormSet, ProductForm
from .models import Box, Order, Product
from .services.box_recommendation import RecommendationInputError

# ---------------------------------------------------------------- dashboard


class DashboardView(TemplateView):
    template_name = "warehouse/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            product_count=Product.objects.count(),
            box_count=Box.objects.count(),
            order_count=Order.objects.count(),
            recent_orders=Order.objects.prefetch_related("items__product")[:5],
        )
        return context


# ----------------------------------------------------------- shared helpers


class FormPageMixin:
    """Supplies the title / cancel link used by the shared form template."""

    template_name = "warehouse/object_form.html"
    page_title = ""
    cancel_url = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["cancel_url"] = self.cancel_url or self.success_url
        return context


class SafeDeleteView(DeleteView):
    """Delete view that reports (rather than crashes on) protected objects."""

    template_name = "warehouse/confirm_delete.html"
    success_message = "Deleted %(name)s."
    protected_message = "%(name)s cannot be deleted because it is used by existing orders."

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cancel_url"] = self.object.get_absolute_url()
        return context

    def form_valid(self, form):
        name = str(self.object)
        success_url = self.get_success_url()
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, self.protected_message % {"name": name})
            return redirect(self.object.get_absolute_url())
        messages.success(self.request, self.success_message % {"name": name})
        return HttpResponseRedirect(success_url)


# ----------------------------------------------------------------- products


class ProductListView(ListView):
    model = Product
    paginate_by = 25


class ProductDetailView(DetailView):
    model = Product


class ProductCreateView(SuccessMessageMixin, FormPageMixin, CreateView):
    model = Product
    form_class = ProductForm
    page_title = "Add product"
    success_url = reverse_lazy("warehouse:product_list")
    success_message = "Product '%(name)s' was created."


class ProductUpdateView(SuccessMessageMixin, FormPageMixin, UpdateView):
    model = Product
    form_class = ProductForm
    page_title = "Edit product"
    success_message = "Product '%(name)s' was updated."

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        self.cancel_url = self.object.get_absolute_url()
        return super().get_context_data(**kwargs)


class ProductDeleteView(SafeDeleteView):
    model = Product
    success_url = reverse_lazy("warehouse:product_list")


# -------------------------------------------------------------------- boxes


class BoxListView(ListView):
    model = Box
    paginate_by = 25


class BoxDetailView(DetailView):
    model = Box


class BoxCreateView(SuccessMessageMixin, FormPageMixin, CreateView):
    model = Box
    form_class = BoxForm
    page_title = "Add box"
    success_url = reverse_lazy("warehouse:box_list")
    success_message = "Box '%(name)s' was created."


class BoxUpdateView(SuccessMessageMixin, FormPageMixin, UpdateView):
    model = Box
    form_class = BoxForm
    page_title = "Edit box"
    success_message = "Box '%(name)s' was updated."

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        self.cancel_url = self.object.get_absolute_url()
        return super().get_context_data(**kwargs)


class BoxDeleteView(SafeDeleteView):
    model = Box
    success_url = reverse_lazy("warehouse:box_list")


# ------------------------------------------------------------------- orders


class OrderListView(ListView):
    model = Order
    paginate_by = 25

    def get_queryset(self):
        return Order.objects.prefetch_related("items__product")


class OrderDetailView(DetailView):
    model = Order

    def get_queryset(self):
        return Order.objects.prefetch_related("items__product")


class OrderDeleteView(SafeDeleteView):
    model = Order
    success_url = reverse_lazy("warehouse:order_list")


def order_create(request):
    """Create an order and its items atomically from a form + formset."""
    if not Product.objects.exists():
        messages.warning(request, "Add at least one product before creating an order.")
        return render(request, "warehouse/order_form.html", {"no_products": True})

    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST, instance=Order())
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                order = form.save()
                formset.instance = order
                formset.save()
            messages.success(request, f"Order #{order.pk} was created.")
            return redirect(order)
        messages.error(request, "Please correct the errors below.")
    else:
        form = OrderForm()
        formset = OrderItemFormSet(instance=Order())

    return render(request, "warehouse/order_form.html", {"form": form, "formset": formset})


class OrderRecommendationView(DetailView):
    """Runs the recommendation engine for one order and shows the outcome."""

    model = Order
    template_name = "warehouse/order_recommendation.html"

    def get_queryset(self):
        return Order.objects.prefetch_related("items__product")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["result"] = self.object.recommend_box()
        except RecommendationInputError as error:
            context["input_error"] = str(error)
        return context

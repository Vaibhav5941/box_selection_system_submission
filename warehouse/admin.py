"""Django admin registrations (used after ``createsuperuser``)."""

from django.contrib import admin

from .models import Box, Order, OrderItem, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "length", "width", "height", "weight")
    search_fields = ("name", "sku")


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ("name", "length", "width", "height", "max_weight", "cost")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("__str__", "created_at")
    inlines = [OrderItemInline]

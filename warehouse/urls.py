"""URL routes for the warehouse app."""

from django.urls import path

from . import views

app_name = "warehouse"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    # Products
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/new/", views.ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    # Boxes
    path("boxes/", views.BoxListView.as_view(), name="box_list"),
    path("boxes/new/", views.BoxCreateView.as_view(), name="box_create"),
    path("boxes/<int:pk>/", views.BoxDetailView.as_view(), name="box_detail"),
    path("boxes/<int:pk>/edit/", views.BoxUpdateView.as_view(), name="box_update"),
    path("boxes/<int:pk>/delete/", views.BoxDeleteView.as_view(), name="box_delete"),
    # Orders
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/new/", views.order_create, name="order_create"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/delete/", views.OrderDeleteView.as_view(), name="order_delete"),
    path(
        "orders/<int:pk>/recommendation/",
        views.OrderRecommendationView.as_view(),
        name="order_recommendation",
    ),
]

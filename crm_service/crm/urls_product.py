"""
Product URLs for CRM
Query endpoints for inventory service
"""
from django.urls import path
from crm_service.crm.views.product_views import (
    search_products,
    get_product,
    list_products_for_sale,
    get_products_bulk,
    check_stock,
)

urlpatterns = [
    path("", list_products_for_sale, name="list_products_for_sale"),
    path("search/", search_products, name="search_products"),
    path("bulk/", get_products_bulk, name="get_products_bulk"),
    path("<uuid:product_id>/", get_product, name="get_product"),
    path("<uuid:product_id>/stock/", check_stock, name="check_stock"),
]

from django.urls import path
from .views.sales_views import (
    commission_rule_list_create, convert_quote_to_order,
    invoice_sales_order, order_detail, order_list_create,
    quotation_detail, quotation_list_create,
    revenue_forecast, target_list_create,
)

urlpatterns = [
    path("quotations/", quotation_list_create),
    path("quotations/<uuid:pk>/", quotation_detail),
    path("quotations/<uuid:pk>/convert/", convert_quote_to_order),
    path("orders/", order_list_create),
    path("orders/<uuid:pk>/", order_detail),
    path("orders/<uuid:pk>/invoice/", invoice_sales_order),
    path("targets/", target_list_create),
    path("commission-rules/", commission_rule_list_create),
    path("forecast/", revenue_forecast),
]

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", lambda request: __import__("django.http", fromlist=["JsonResponse"]).JsonResponse({"status": "ok"})),
    path("api/crm/contacts/", include("crm_service.contacts.urls")),
    path("api/crm/pipeline/", include("crm_service.pipeline.urls")),
    path("api/crm/campaigns/", include("crm_service.campaigns.urls")),
    path("api/crm/sales/", include("crm_service.sales.urls")),
    path("api/crm/product-catalog/", include("crm_service.crm.urls_product")),  # Product query endpoints
]

from django.urls import path
from .views import (
    lead_detail, lead_list_create, opportunity_detail, opportunity_list_create,
    pipeline_overview, stage_detail, stage_list_create,
)

urlpatterns = [
    path("stages/", stage_list_create),
    path("stages/<uuid:pk>/", stage_detail),
    path("leads/", lead_list_create),
    path("leads/<uuid:pk>/", lead_detail),
    path("opportunities/", opportunity_list_create),
    path("opportunities/<uuid:pk>/", opportunity_detail),
    path("overview/", pipeline_overview),
]

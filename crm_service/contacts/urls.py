from django.urls import path
from .views import (
    activity_detail, activity_list_create, company_detail,
    company_list_create, contact_detail, contact_list_create, tag_list_create,
)

urlpatterns = [
    path("", contact_list_create),
    path("<uuid:pk>/", contact_detail),
    path("<uuid:pk>/activities/", activity_list_create),
    path("companies/", company_list_create),
    path("companies/<uuid:pk>/", company_detail),
    path("activities/", activity_list_create),
    path("activities/<uuid:pk>/", activity_detail),
    path("tags/", tag_list_create),
]

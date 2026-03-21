from django.urls import path
from .views import add_campaign_member, campaign_detail, campaign_list_create, template_list_create

urlpatterns = [
    path("templates/", template_list_create),
    path("", campaign_list_create),
    path("<uuid:pk>/", campaign_detail),
    path("<uuid:pk>/members/", add_campaign_member),
]

from django.contrib import admin
from .models import Company, Contact, Activity, Tag

admin.site.register(Tag)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "industry", "city", "is_customer"]
    search_fields = ["name", "email"]

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "company", "is_active"]
    search_fields = ["first_name", "last_name", "email"]

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["subject", "activity_type", "status", "scheduled_at"]
    list_filter = ["activity_type", "status"]

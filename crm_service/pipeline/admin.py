from django.contrib import admin
from .models import Lead, Opportunity, PipelineStage, LeadSource

admin.site.register(PipelineStage)
admin.site.register(LeadSource)

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "state", "score", "created_at"]
    list_filter = ["state"]

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ["name", "stage", "expected_revenue", "probability", "expected_close_date"]
    list_filter = ["stage", "priority"]

from django.contrib import admin
from .models import CommissionRule, Quotation, SalesOrder, SalesTarget

@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ["quote_number", "version", "state", "total_amount", "created_at"]
    list_filter = ["state"]

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "state", "total_amount", "created_at"]
    list_filter = ["state"]

admin.site.register(SalesTarget)
admin.site.register(CommissionRule)

from rest_framework import serializers
from .models import (
    CommissionPayout, CommissionRule, Quotation, QuotationLine,
    SalesOrder, SalesOrderLine, SalesTarget,
)


class QuotationLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuotationLine
        fields = [
            "id", "product_id", "description", "quantity", "unit_price",
            "discount_percent", "discount_amount", "tax_rate", "tax_amount",
            "subtotal", "sequence",
        ]
        read_only_fields = ["id", "discount_amount", "tax_amount", "subtotal"]


class QuotationSerializer(serializers.ModelSerializer):
    lines = QuotationLineSerializer(many=True, read_only=True)
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only=True)

    class Meta:
        model = Quotation
        fields = [
            "id", "corporate_id", "quote_number", "version", "state",
            "contact", "contact_name", "company", "company_name", "opportunity",
            "valid_until", "currency", "subtotal", "discount_amount",
            "tax_amount", "total_amount", "terms", "notes", "signature_url",
            "signed_at", "assigned_to", "created_at", "updated_at", "lines",
        ]
        read_only_fields = ["id", "quote_number", "subtotal", "discount_amount", "tax_amount", "total_amount", "created_at", "updated_at"]

    def get_contact_name(self, obj):
        return str(obj.contact) if obj.contact else None


class SalesOrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderLine
        fields = ["id", "product_id", "description", "quantity", "unit_price", "discount_percent", "tax_rate", "subtotal"]
        read_only_fields = ["id", "subtotal"]


class SalesOrderSerializer(serializers.ModelSerializer):
    lines = SalesOrderLineSerializer(many=True, read_only=True)
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only=True)
    state_display = serializers.CharField(source="get_state_display", read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            "id", "corporate_id", "order_number", "state", "state_display",
            "quotation", "contact", "contact_name", "company", "company_name",
            "currency", "payment_terms_days", "delivery_date", "delivery_address",
            "subtotal", "discount_amount", "tax_amount", "total_amount",
            "invoice_ref", "notes", "created_by", "assigned_to",
            "created_at", "updated_at", "lines",
        ]
        read_only_fields = ["id", "order_number", "subtotal", "discount_amount", "tax_amount", "total_amount", "created_at", "updated_at"]

    def get_contact_name(self, obj):
        return str(obj.contact) if obj.contact else None


class SalesTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesTarget
        fields = ["id", "name", "period_type", "start_date", "end_date", "assigned_to", "target_amount", "currency", "created_at"]
        read_only_fields = ["id", "created_at"]


class CommissionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionRule
        fields = ["id", "name", "commission_percent", "min_amount", "max_amount", "is_active"]
        read_only_fields = ["id"]


class CommissionPayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommissionPayout
        fields = ["id", "sales_order", "rep_id", "rule", "order_amount", "commission_amount", "state", "paid_at", "created_at"]
        read_only_fields = ["id", "commission_amount", "created_at"]

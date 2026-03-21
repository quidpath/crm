from rest_framework import serializers
from .models import Lead, LeadSource, Opportunity, PipelineStage


class PipelineStageSerializer(serializers.ModelSerializer):
    opportunity_count = serializers.SerializerMethodField()

    class Meta:
        model = PipelineStage
        fields = ["id", "name", "sequence", "probability", "is_won", "is_lost", "opportunity_count"]
        read_only_fields = ["id"]

    def get_opportunity_count(self, obj):
        return obj.opportunities.count()


class LeadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadSource
        fields = ["id", "name"]
        read_only_fields = ["id"]


class LeadSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source="source.name", read_only=True)

    class Meta:
        model = Lead
        fields = [
            "id", "name", "contact_name", "email", "phone", "company_name",
            "source", "source_name", "state", "score", "estimated_value",
            "description", "assigned_to", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OpportunitySerializer(serializers.ModelSerializer):
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    contact_name = serializers.SerializerMethodField()
    company_name = serializers.CharField(source="company.name", read_only=True)
    weighted_revenue = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id", "corporate_id", "name", "contact", "contact_name", "company",
            "company_name", "lead", "stage", "stage_name", "priority",
            "expected_revenue", "probability", "weighted_revenue",
            "expected_close_date", "description", "loss_reason",
            "assigned_to", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "weighted_revenue", "created_at", "updated_at"]

    def get_contact_name(self, obj):
        return str(obj.contact) if obj.contact else None

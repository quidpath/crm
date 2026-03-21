from rest_framework import serializers
from .models import Campaign, CampaignMember, EmailTemplate


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ["id", "name", "subject", "body_html", "body_text", "created_at"]
        read_only_fields = ["id", "created_at"]


class CampaignMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignMember
        fields = ["id", "contact", "status", "sent_at", "opened_at", "clicked_at", "notes"]
        read_only_fields = ["id"]


class CampaignSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            "id", "name", "campaign_type", "state", "template", "description",
            "start_date", "end_date", "budget", "created_at", "member_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_member_count(self, obj):
        return obj.members.count()

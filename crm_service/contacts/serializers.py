from rest_framework import serializers
from .models import Activity, Company, Contact, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color"]


class CompanySerializer(serializers.ModelSerializer):
    tag_details = TagSerializer(source="tags", many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            "id", "corporate_id", "name", "industry", "website", "phone", "email",
            "address", "city", "country", "employee_count", "annual_revenue",
            "description", "tags", "tag_details", "assigned_to", "is_customer",
            "is_supplier", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ContactSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    company_name = serializers.CharField(source="company.name", read_only=True)
    tag_details = TagSerializer(source="tags", many=True, read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id", "corporate_id", "company", "company_name", "salutation",
            "first_name", "last_name", "full_name", "email", "phone", "mobile",
            "job_title", "department", "address", "city", "country",
            "linkedin", "twitter", "description", "tags", "tag_details",
            "assigned_to", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "full_name", "created_at", "updated_at"]


class ActivitySerializer(serializers.ModelSerializer):
    activity_type_display = serializers.CharField(source="get_activity_type_display", read_only=True)
    contact_name = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id", "activity_type", "activity_type_display", "status", "subject",
            "description", "contact", "contact_name", "company", "scheduled_at",
            "done_at", "duration_minutes", "assigned_to", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_contact_name(self, obj):
        return str(obj.contact) if obj.contact else None

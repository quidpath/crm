from django.db import models

from crm_service.core.base_models import BaseModel


class EmailTemplate(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=300)
    body_html = models.TextField()
    body_text = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Campaign(BaseModel):
    STATES = [("draft", "Draft"), ("active", "Active"), ("paused", "Paused"), ("completed", "Completed")]
    TYPES = [("email", "Email"), ("sms", "SMS"), ("phone", "Phone Call"), ("event", "Event")]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=TYPES, default="email")
    state = models.CharField(max_length=20, choices=STATES, default="draft")
    template = models.ForeignKey(EmailTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.UUIDField(null=True, blank=True)

    def __str__(self):
        return self.name


class CampaignMember(BaseModel):
    STATUSES = [("pending", "Pending"), ("sent", "Sent"), ("opened", "Opened"), ("clicked", "Clicked"), ("replied", "Replied"), ("unsubscribed", "Unsubscribed")]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="members")
    contact = models.ForeignKey("contacts.Contact", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUSES, default="pending")
    sent_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=300, blank=True)

    class Meta:
        unique_together = [("campaign", "contact")]

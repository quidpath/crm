from decimal import Decimal
from django.db import models

from crm_service.core.base_models import BaseModel


class PipelineStage(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=100)
    sequence = models.PositiveIntegerField(default=10)
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("50"))
    is_won = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)

    class Meta:
        ordering = ["sequence"]

    def __str__(self):
        return self.name


class LeadSource(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Lead(BaseModel):
    STATES = [("new", "New"), ("qualified", "Qualified"), ("converted", "Converted"), ("lost", "Lost")]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=300, help_text="Lead/Company name")
    contact_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True, db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    company_name = models.CharField(max_length=300, blank=True)
    source = models.ForeignKey(LeadSource, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATES, default="new")
    score = models.PositiveIntegerField(default=0, help_text="Lead score 0-100")
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    description = models.TextField(blank=True)
    assigned_to = models.UUIDField(null=True, blank=True)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Opportunity(BaseModel):
    PRIORITIES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=300)
    contact = models.ForeignKey("contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True, related_name="opportunities")
    company = models.ForeignKey("contacts.Company", on_delete=models.SET_NULL, null=True, blank=True, related_name="opportunities")
    lead = models.ForeignKey(Lead, on_delete=models.SET_NULL, null=True, blank=True)
    stage = models.ForeignKey(PipelineStage, on_delete=models.PROTECT, related_name="opportunities")
    priority = models.CharField(max_length=10, choices=PRIORITIES, default="medium")
    expected_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    probability = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("50"))
    expected_close_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    loss_reason = models.TextField(blank=True)
    assigned_to = models.UUIDField(null=True, blank=True)
    tags = models.ManyToManyField("contacts.Tag", blank=True)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-expected_revenue"]

    def __str__(self):
        return self.name

    @property
    def weighted_revenue(self):
        return self.expected_revenue * self.probability / Decimal("100")

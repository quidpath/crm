from decimal import Decimal
from django.db import models

from crm_service.core.base_models import BaseModel


class Quotation(BaseModel):
    STATES = [
        ("draft", "Draft"),
        ("sent", "Sent to Customer"),
        ("accepted", "Accepted"),
        ("cancelled", "Cancelled"),
        ("expired", "Expired"),
    ]

    corporate_id = models.UUIDField(db_index=True)
    quote_number = models.CharField(max_length=100, unique=True)
    version = models.PositiveIntegerField(default=1)
    state = models.CharField(max_length=20, choices=STATES, default="draft")
    contact = models.ForeignKey("contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey("contacts.Company", on_delete=models.SET_NULL, null=True, blank=True)
    opportunity = models.ForeignKey("pipeline.Opportunity", on_delete=models.SET_NULL, null=True, blank=True)
    valid_until = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3, default="KES")
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    terms = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    signature_url = models.URLField(blank=True, help_text="e-signature URL or file path")
    signed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.UUIDField(null=True, blank=True)
    assigned_to = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.quote_number} v{self.version}"

    def recalculate(self):
        lines = self.lines.all()
        self.subtotal = sum(l.subtotal for l in lines)
        self.discount_amount = sum(l.discount_amount for l in lines)
        self.tax_amount = sum(l.tax_amount for l in lines)
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        self.save()


class QuotationLine(BaseModel):
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name="lines")
    product_id = models.UUIDField(null=True, blank=True)
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1"))
    unit_price = models.DecimalField(max_digits=14, decimal_places=4)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("16"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    sequence = models.PositiveIntegerField(default=10)

    def save(self, *args, **kwargs):
        gross = self.quantity * self.unit_price
        self.discount_amount = gross * self.discount_percent / Decimal("100")
        net = gross - self.discount_amount
        self.tax_amount = net * self.tax_rate / Decimal("100")
        self.subtotal = gross
        super().save(*args, **kwargs)


class SalesOrder(BaseModel):
    STATES = [
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("invoiced", "Invoiced"),
        ("cancelled", "Cancelled"),
    ]

    corporate_id = models.UUIDField(db_index=True)
    order_number = models.CharField(max_length=100, unique=True)
    state = models.CharField(max_length=20, choices=STATES, default="draft")
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    contact = models.ForeignKey("contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True)
    company = models.ForeignKey("contacts.Company", on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.CharField(max_length=3, default="KES")
    payment_terms_days = models.PositiveIntegerField(default=30)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_address = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    discount_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    invoice_ref = models.CharField(max_length=100, blank=True, help_text="Invoice reference from Accounting")
    notes = models.TextField(blank=True)
    created_by = models.UUIDField(null=True, blank=True)
    assigned_to = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


class SalesOrderLine(BaseModel):
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="lines")
    product_id = models.UUIDField(null=True, blank=True)
    description = models.CharField(max_length=500)
    quantity = models.DecimalField(max_digits=14, decimal_places=4, default=Decimal("1"))
    unit_price = models.DecimalField(max_digits=14, decimal_places=4)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("16"))
    subtotal = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))

    def save(self, *args, **kwargs):
        gross = self.quantity * self.unit_price
        discount = gross * self.discount_percent / Decimal("100")
        self.subtotal = gross - discount
        super().save(*args, **kwargs)


class SalesTarget(BaseModel):
    PERIOD_TYPES = [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    assigned_to = models.UUIDField(null=True, blank=True, help_text="Rep or team")
    target_amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=3, default="KES")

    def __str__(self):
        return self.name


class CommissionRule(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=200)
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2)
    min_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    max_amount = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}: {self.commission_percent}%"


class CommissionPayout(BaseModel):
    STATES = [("pending", "Pending"), ("approved", "Approved"), ("paid", "Paid")]

    corporate_id = models.UUIDField(db_index=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="commissions")
    rep_id = models.UUIDField()
    rule = models.ForeignKey(CommissionRule, on_delete=models.PROTECT)
    order_amount = models.DecimalField(max_digits=14, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=14, decimal_places=2)
    state = models.CharField(max_length=20, choices=STATES, default="pending")
    paid_at = models.DateTimeField(null=True, blank=True)

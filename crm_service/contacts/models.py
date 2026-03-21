from django.db import models

from crm_service.core.base_models import BaseModel


class Tag(BaseModel):
    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default="#6B7280")

    class Meta:
        unique_together = [("corporate_id", "name")]

    def __str__(self):
        return self.name


class Company(BaseModel):
    INDUSTRIES = [
        ("technology", "Technology"), ("finance", "Finance"), ("healthcare", "Healthcare"),
        ("manufacturing", "Manufacturing"), ("retail", "Retail"), ("education", "Education"),
        ("real_estate", "Real Estate"), ("hospitality", "Hospitality"), ("agriculture", "Agriculture"),
        ("other", "Other"),
    ]

    corporate_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=300, db_index=True)
    industry = models.CharField(max_length=50, choices=INDUSTRIES, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Kenya")
    employee_count = models.PositiveIntegerField(null=True, blank=True)
    annual_revenue = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    assigned_to = models.UUIDField(null=True, blank=True, help_text="Sales rep user_id")
    is_customer = models.BooleanField(default=False)
    is_supplier = models.BooleanField(default=False)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(BaseModel):
    SALUTATIONS = [("Mr", "Mr."), ("Mrs", "Mrs."), ("Ms", "Ms."), ("Dr", "Dr."), ("Prof", "Prof.")]

    corporate_id = models.UUIDField(db_index=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="contacts")
    salutation = models.CharField(max_length=10, choices=SALUTATIONS, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, db_index=True)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    department = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Kenya")
    linkedin = models.URLField(blank=True)
    twitter = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    assigned_to = models.UUIDField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.salutation} {self.first_name} {self.last_name}".strip()


class Activity(BaseModel):
    ACTIVITY_TYPES = [
        ("call", "Phone Call"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("task", "Task"),
        ("note", "Note"),
        ("demo", "Demo"),
        ("follow_up", "Follow-up"),
    ]
    STATUSES = [("planned", "Planned"), ("done", "Done"), ("cancelled", "Cancelled")]

    corporate_id = models.UUIDField(db_index=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    status = models.CharField(max_length=20, choices=STATUSES, default="planned")
    subject = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="activities")
    scheduled_at = models.DateTimeField(null=True, blank=True)
    done_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    assigned_to = models.UUIDField(null=True, blank=True)
    created_by = models.UUIDField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_activity_type_display()}: {self.subject}"

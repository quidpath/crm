from django.contrib import admin
from .models import Campaign, CampaignMember, EmailTemplate
admin.site.register(EmailTemplate)
admin.site.register(Campaign)
admin.site.register(CampaignMember)

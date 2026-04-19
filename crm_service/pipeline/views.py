from decimal import Decimal
from django.db.models import Sum, Count, Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Lead, LeadSource, Opportunity, PipelineStage
from .serializers import LeadSerializer, LeadSourceSerializer, OpportunitySerializer, PipelineStageSerializer
from crm_service.core.utils.pagination import paginate_qs


@api_view(["GET", "POST"])
def stage_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(PipelineStageSerializer(PipelineStage.objects.filter(corporate_id=cid), many=True).data)
    s = PipelineStageSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def stage_detail(request, pk):
    cid = request.corporate_id
    try:
        stage = PipelineStage.objects.get(pk=pk, corporate_id=cid)
    except PipelineStage.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(PipelineStageSerializer(stage).data)
    if request.method in ("PUT", "PATCH"):
        s = PipelineStageSerializer(stage, data=request.data, partial=request.method == "PATCH")
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    stage.delete()
    return Response(status=204)


@api_view(["GET", "POST"])
def lead_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = Lead.objects.filter(corporate_id=cid)
        state = request.GET.get("state")
        if state:
            qs = qs.filter(state=state)
        search = request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search) | Q(phone__icontains=search))
        qs = qs.order_by("-created_at")
        page_qs, meta = paginate_qs(qs, request)
        return Response({"results": LeadSerializer(page_qs, many=True).data, **meta})
    s = LeadSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def lead_detail(request, pk):
    cid = request.corporate_id
    try:
        lead = Lead.objects.get(pk=pk, corporate_id=cid)
    except Lead.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(LeadSerializer(lead).data)
    if request.method in ("PUT", "PATCH"):
        s = LeadSerializer(lead, data=request.data, partial=request.method == "PATCH")
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    lead.delete()
    return Response(status=204)


@api_view(["GET", "POST"])
def opportunity_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = Opportunity.objects.filter(corporate_id=cid).select_related("stage", "contact", "company")
        stage_id = request.GET.get("stage")
        if stage_id:
            qs = qs.filter(stage_id=stage_id)
        assigned = request.GET.get("assigned_to")
        if assigned:
            qs = qs.filter(assigned_to=assigned)
        search = request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(contact__first_name__icontains=search) | Q(contact__last_name__icontains=search))
        qs = qs.order_by("-created_at")
        page_qs, meta = paginate_qs(qs, request)
        return Response({"results": OpportunitySerializer(page_qs, many=True).data, **meta})
    s = OpportunitySerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH"])
def opportunity_detail(request, pk):
    cid = request.corporate_id
    try:
        opp = Opportunity.objects.get(pk=pk, corporate_id=cid)
    except Opportunity.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(OpportunitySerializer(opp).data)
    s = OpportunitySerializer(opp, data=request.data, partial=request.method == "PATCH")
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["GET"])
def pipeline_overview(request):
    """
    CRM Dashboard Summary with period-over-period comparisons.
    Returns metrics for contacts, deals, pipeline value, and conversion rate.
    """
    from datetime import datetime, timedelta
    from django.utils import timezone
    from crm_service.contacts.models import Contact
    
    cid = request.corporate_id
    
    # Current period (this month)
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Previous period (last month)
    if month_start.month == 1:
        prev_month_start = month_start.replace(year=month_start.year - 1, month=12)
    else:
        prev_month_start = month_start.replace(month=month_start.month - 1)
    prev_month_end = month_start - timedelta(seconds=1)
    
    # Helper functions for calculations
    def calc_change(current, previous):
        if previous > 0:
            return round(float(((current - previous) / previous) * 100), 1)
        return 0.0
    
    def get_trend(change):
        if change > 0:
            return "up"
        elif change < 0:
            return "down"
        return "neutral"
    
    # Total Contacts
    total_contacts = Contact.objects.filter(corporate_id=cid).count()
    prev_contacts = Contact.objects.filter(
        corporate_id=cid,
        created_at__lt=month_start
    ).count()
    contacts_change = calc_change(total_contacts, prev_contacts)
    
    # Total Deals (Opportunities) - open deals are those not won or lost
    total_deals = Opportunity.objects.filter(
        corporate_id=cid,
        stage__is_won=False,
        stage__is_lost=False
    ).count()
    prev_deals = Opportunity.objects.filter(
        corporate_id=cid,
        stage__is_won=False,
        stage__is_lost=False,
        created_at__lt=month_start
    ).count()
    deals_change = calc_change(total_deals, prev_deals)
    
    # Pipeline Value - only open deals
    pipeline_value = Opportunity.objects.filter(
        corporate_id=cid,
        stage__is_won=False,
        stage__is_lost=False
    ).aggregate(total=Sum('expected_revenue'))['total'] or Decimal('0')
    
    prev_pipeline_value = Opportunity.objects.filter(
        corporate_id=cid,
        stage__is_won=False,
        stage__is_lost=False,
        created_at__lt=month_start
    ).aggregate(total=Sum('expected_revenue'))['total'] or Decimal('0')
    
    pipeline_change = calc_change(float(pipeline_value), float(prev_pipeline_value))
    
    # Won Deals This Month
    won_deals_this_month = Opportunity.objects.filter(
        corporate_id=cid,
        stage__is_won=True,
        updated_at__gte=month_start
    ).count()
    
    # Conversion Rate (won deals / total closed deals)
    total_closed_deals = Opportunity.objects.filter(
        corporate_id=cid
    ).filter(
        Q(stage__is_won=True) | Q(stage__is_lost=True)
    ).count()
    won_deals_all = Opportunity.objects.filter(
        corporate_id=cid,
        stage__is_won=True
    ).count()
    conversion_rate = round((won_deals_all / total_closed_deals * 100), 1) if total_closed_deals > 0 else 0
    
    # Previous conversion rate
    prev_closed_deals = Opportunity.objects.filter(
        corporate_id=cid,
        updated_at__lt=month_start
    ).filter(
        Q(stage__is_won=True) | Q(stage__is_lost=True)
    ).count()
    prev_won_deals = Opportunity.objects.filter(
        corporate_id=cid,
        stage__is_won=True,
        updated_at__lt=month_start
    ).count()
    prev_conversion_rate = round((prev_won_deals / prev_closed_deals * 100), 1) if prev_closed_deals > 0 else 0
    conversion_change = calc_change(conversion_rate, prev_conversion_rate)
    
    # Active Campaigns
    from crm_service.campaigns.models import Campaign
    active_campaigns = Campaign.objects.filter(
        corporate_id=cid,
        state='active'
    ).count()
    
    # Pipeline stages breakdown
    stages = PipelineStage.objects.filter(corporate_id=cid).annotate(
        count=Count("opportunities"),
        total_value=Sum("opportunities__expected_revenue"),
    )
    stages_data = []
    for s in stages:
        stages_data.append({
            "stage_id": str(s.id),
            "stage_name": s.name,
            "sequence": s.sequence,
            "opportunity_count": s.count,
            "total_value": str(s.total_value or 0),
            "probability": str(s.probability),
        })
    
    return Response({
        # Summary metrics with comparisons
        "total_contacts": total_contacts,
        "total_contacts_previous": prev_contacts,
        "total_contacts_change": contacts_change,
        "total_contacts_trend": get_trend(contacts_change),
        
        "total_deals": total_deals,
        "total_deals_previous": prev_deals,
        "total_deals_change": deals_change,
        "total_deals_trend": get_trend(deals_change),
        
        "pipeline_value": float(pipeline_value),
        "pipeline_value_previous": float(prev_pipeline_value),
        "pipeline_value_change": pipeline_change,
        "pipeline_value_trend": get_trend(pipeline_change),
        
        "won_deals_this_month": won_deals_this_month,
        
        "conversion_rate": conversion_rate,
        "conversion_rate_previous": prev_conversion_rate,
        "conversion_rate_change": conversion_change,
        "conversion_rate_trend": get_trend(conversion_change),
        
        "active_campaigns": active_campaigns,
        
        # Pipeline stages breakdown
        "stages": stages_data,
        "grand_total": str(pipeline_value),
    })

from decimal import Decimal
from django.db.models import Sum, Count, Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Lead, LeadSource, Opportunity, PipelineStage
from .serializers import LeadSerializer, LeadSourceSerializer, OpportunitySerializer, PipelineStageSerializer


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
        search = request.GET.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))
        return Response(LeadSerializer(qs, many=True).data)
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
        return Response(OpportunitySerializer(qs, many=True).data)
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
    """Pipeline summary by stage — for Kanban/funnel view."""
    cid = request.corporate_id
    stages = PipelineStage.objects.filter(corporate_id=cid).annotate(
        count=Count("opportunities"),
        total_value=Sum("opportunities__expected_revenue"),
    )
    data = []
    for s in stages:
        data.append({
            "stage_id": str(s.id),
            "stage_name": s.name,
            "sequence": s.sequence,
            "opportunity_count": s.count,
            "total_value": str(s.total_value or 0),
            "probability": str(s.probability),
        })
    grand_total = Opportunity.objects.filter(
        corporate_id=cid
    ).aggregate(t=Sum("expected_revenue"))["t"] or Decimal("0")
    return Response({"stages": data, "grand_total": str(grand_total)})

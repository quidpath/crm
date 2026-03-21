from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Campaign, CampaignMember, EmailTemplate
from .serializers import CampaignMemberSerializer, CampaignSerializer, EmailTemplateSerializer


@api_view(["GET", "POST"])
def template_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(EmailTemplateSerializer(EmailTemplate.objects.filter(corporate_id=cid), many=True).data)
    s = EmailTemplateSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def campaign_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(CampaignSerializer(Campaign.objects.filter(corporate_id=cid), many=True).data)
    s = CampaignSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PATCH"])
def campaign_detail(request, pk):
    cid = request.corporate_id
    try:
        camp = Campaign.objects.get(pk=pk, corporate_id=cid)
    except Campaign.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        data = CampaignSerializer(camp).data
        data["members"] = CampaignMemberSerializer(camp.members.all(), many=True).data
        return Response(data)
    s = CampaignSerializer(camp, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["POST"])
def add_campaign_member(request, pk):
    cid = request.corporate_id
    try:
        camp = Campaign.objects.get(pk=pk, corporate_id=cid)
    except Campaign.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    s = CampaignMemberSerializer(data=request.data)
    if s.is_valid():
        s.save(campaign=camp)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)

from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Activity, Company, Contact, Tag
from .serializers import ActivitySerializer, CompanySerializer, ContactSerializer, TagSerializer
from crm_service.core.utils.pagination import paginate_qs


@api_view(["GET", "POST"])
def contact_list_create(request):
    corporate_id = request.corporate_id
    if request.method == "GET":
        qs = Contact.objects.filter(corporate_id=corporate_id).select_related("company")
        search = request.GET.get("search", "").strip()
        if search:
            qs = qs.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search)
            )
        company_id = request.GET.get("company")
        if company_id:
            qs = qs.filter(company_id=company_id)
        contact_type = request.GET.get("type")
        if contact_type:
            qs = qs.filter(contact_type=contact_type)
        qs = qs.order_by("-created_at")
        page_qs, meta = paginate_qs(qs, request)
        return Response({"results": ContactSerializer(page_qs, many=True).data, **meta})
    s = ContactSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=corporate_id, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def contact_detail(request, pk):
    corporate_id = request.corporate_id
    try:
        contact = Contact.objects.get(pk=pk, corporate_id=corporate_id)
    except Contact.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(ContactSerializer(contact).data)
    if request.method in ("PUT", "PATCH"):
        s = ContactSerializer(contact, data=request.data, partial=request.method == "PATCH")
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    contact.is_active = False
    contact.save()
    return Response(status=204)


@api_view(["GET", "POST"])
def company_list_create(request):
    corporate_id = request.corporate_id
    if request.method == "GET":
        qs = Company.objects.filter(corporate_id=corporate_id)
        search = request.GET.get("search")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(email__icontains=search))
        return Response(CompanySerializer(qs, many=True).data)
    s = CompanySerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=corporate_id, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def company_detail(request, pk):
    corporate_id = request.corporate_id
    try:
        company = Company.objects.get(pk=pk, corporate_id=corporate_id)
    except Company.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(CompanySerializer(company).data)
    if request.method in ("PUT", "PATCH"):
        s = CompanySerializer(company, data=request.data, partial=request.method == "PATCH")
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)
    company.delete()
    return Response(status=204)


@api_view(["GET", "POST"])
def activity_list_create(request):
    corporate_id = request.corporate_id
    if request.method == "GET":
        qs = Activity.objects.filter(corporate_id=corporate_id)
        contact_id = request.GET.get("contact")
        if contact_id:
            qs = qs.filter(contact_id=contact_id)
        company_id = request.GET.get("company")
        if company_id:
            qs = qs.filter(company_id=company_id)
        activity_type = request.GET.get("type")
        if activity_type:
            qs = qs.filter(activity_type=activity_type)
        return Response(ActivitySerializer(qs[:100], many=True).data)
    s = ActivitySerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=corporate_id, created_by=request.user_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "PATCH"])
def activity_detail(request, pk):
    corporate_id = request.corporate_id
    try:
        activity = Activity.objects.get(pk=pk, corporate_id=corporate_id)
    except Activity.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(ActivitySerializer(activity).data)
    s = ActivitySerializer(activity, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def tag_list_create(request):
    corporate_id = request.corporate_id
    if request.method == "GET":
        return Response(TagSerializer(Tag.objects.filter(corporate_id=corporate_id), many=True).data)
    s = TagSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=corporate_id)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)

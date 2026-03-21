import logging
import uuid
from decimal import Decimal

from django.db.models import Sum, Count
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from crm_service.sales.models import (
    CommissionPayout, CommissionRule, Quotation, QuotationLine,
    SalesOrder, SalesOrderLine, SalesTarget,
)
from crm_service.sales.serializers import (
    CommissionPayoutSerializer, CommissionRuleSerializer,
    QuotationSerializer, SalesOrderSerializer, SalesTargetSerializer,
)
from crm_service.services.erp_client import ERPClient

logger = logging.getLogger(__name__)
erp_client = ERPClient()


def _ref(prefix, cid):
    return f"{prefix}-{timezone.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"


# ─── Quotations ──────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
def quotation_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = Quotation.objects.filter(corporate_id=cid).select_related("contact", "company")
        state = request.GET.get("state")
        if state:
            qs = qs.filter(state=state)
        return Response(QuotationSerializer(qs, many=True).data)

    quote_number = _ref("QT", cid)
    q = Quotation.objects.create(
        corporate_id=cid,
        quote_number=quote_number,
        contact_id=request.data.get("contact"),
        company_id=request.data.get("company"),
        opportunity_id=request.data.get("opportunity"),
        valid_until=request.data.get("valid_until"),
        currency=request.data.get("currency", "KES"),
        terms=request.data.get("terms", ""),
        notes=request.data.get("notes", ""),
        created_by=request.user_id,
        assigned_to=request.data.get("assigned_to", request.user_id),
    )
    for line_data in request.data.get("lines", []):
        QuotationLine.objects.create(
            quotation=q,
            product_id=line_data.get("product_id"),
            description=line_data["description"],
            quantity=Decimal(str(line_data.get("quantity", "1"))),
            unit_price=Decimal(str(line_data["unit_price"])),
            discount_percent=Decimal(str(line_data.get("discount_percent", "0"))),
            tax_rate=Decimal(str(line_data.get("tax_rate", "16"))),
            sequence=line_data.get("sequence", 10),
        )
    q.recalculate()
    return Response(QuotationSerializer(q).data, status=201)


@api_view(["GET", "PATCH"])
def quotation_detail(request, pk):
    cid = request.corporate_id
    try:
        q = Quotation.objects.get(pk=pk, corporate_id=cid)
    except Quotation.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(QuotationSerializer(q).data)
    s = QuotationSerializer(q, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["POST"])
def convert_quote_to_order(request, pk):
    """Convert an accepted quotation into a sales order."""
    cid = request.corporate_id
    try:
        q = Quotation.objects.get(pk=pk, corporate_id=cid, state="accepted")
    except Quotation.DoesNotExist:
        return Response({"error": "Accepted quotation not found"}, status=404)

    order_number = _ref("SO", cid)
    so = SalesOrder.objects.create(
        corporate_id=cid,
        order_number=order_number,
        quotation=q,
        contact=q.contact,
        company=q.company,
        currency=q.currency,
        payment_terms_days=request.data.get("payment_terms_days", 30),
        delivery_date=request.data.get("delivery_date"),
        delivery_address=request.data.get("delivery_address", ""),
        notes=q.notes,
        created_by=request.user_id,
        assigned_to=q.assigned_to,
    )
    for ql in q.lines.all():
        SalesOrderLine.objects.create(
            order=so,
            product_id=ql.product_id,
            description=ql.description,
            quantity=ql.quantity,
            unit_price=ql.unit_price,
            discount_percent=ql.discount_percent,
            tax_rate=ql.tax_rate,
        )

    so_lines = so.lines.all()
    so.subtotal = sum(l.subtotal for l in so_lines)
    so.total_amount = so.subtotal
    so.state = "confirmed"
    so.save()
    return Response(SalesOrderSerializer(so).data, status=201)


# ─── Sales Orders ────────────────────────────────────────────────────────────

@api_view(["GET", "POST"])
def order_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        qs = SalesOrder.objects.filter(corporate_id=cid).select_related("contact", "company")
        state = request.GET.get("state")
        if state:
            qs = qs.filter(state=state)
        return Response(SalesOrderSerializer(qs, many=True).data)
    order_number = _ref("SO", cid)
    so = SalesOrder.objects.create(
        corporate_id=cid,
        order_number=order_number,
        contact_id=request.data.get("contact"),
        company_id=request.data.get("company"),
        currency=request.data.get("currency", "KES"),
        payment_terms_days=request.data.get("payment_terms_days", 30),
        created_by=request.user_id,
    )
    return Response(SalesOrderSerializer(so).data, status=201)


@api_view(["GET", "PATCH"])
def order_detail(request, pk):
    cid = request.corporate_id
    try:
        so = SalesOrder.objects.get(pk=pk, corporate_id=cid)
    except SalesOrder.DoesNotExist:
        return Response({"error": "Not found"}, status=404)
    if request.method == "GET":
        return Response(SalesOrderSerializer(so).data)
    s = SalesOrderSerializer(so, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response(s.data)
    return Response(s.errors, status=400)


@api_view(["POST"])
def invoice_sales_order(request, pk):
    """Create invoice in ERP Accounting for the sales order."""
    cid = request.corporate_id
    try:
        so = SalesOrder.objects.get(pk=pk, corporate_id=cid, state__in=["confirmed", "delivered"])
    except SalesOrder.DoesNotExist:
        return Response({"error": "Order not found or not in invoiceable state"}, status=404)

    invoice_payload = {
        "corporate_id": str(cid),
        "reference": so.order_number,
        "contact_name": str(so.contact) if so.contact else str(so.company),
        "currency": so.currency,
        "payment_terms_days": so.payment_terms_days,
        "lines": [
            {
                "description": l.description,
                "quantity": str(l.quantity),
                "unit_price": str(l.unit_price),
                "tax_rate": str(l.tax_rate),
            }
            for l in so.lines.all()
        ],
    }
    result = erp_client.create_invoice(invoice_payload)
    if result:
        so.invoice_ref = result.get("invoice_number", "")
        so.state = "invoiced"
        so.save()
        return Response({"invoice": result, "order": SalesOrderSerializer(so).data})
    return Response({"error": "Failed to create invoice in Accounting"}, status=502)


# ─── Sales Targets & Commissions ────────────────────────────────────────────

@api_view(["GET", "POST"])
def target_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(SalesTargetSerializer(SalesTarget.objects.filter(corporate_id=cid), many=True).data)
    s = SalesTargetSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET", "POST"])
def commission_rule_list_create(request):
    cid = request.corporate_id
    if request.method == "GET":
        return Response(CommissionRuleSerializer(CommissionRule.objects.filter(corporate_id=cid, is_active=True), many=True).data)
    s = CommissionRuleSerializer(data=request.data)
    if s.is_valid():
        s.save(corporate_id=cid)
        return Response(s.data, status=201)
    return Response(s.errors, status=400)


@api_view(["GET"])
def revenue_forecast(request):
    """Revenue forecast from open opportunities weighted by probability."""
    cid = request.corporate_id
    from crm_service.pipeline.models import Opportunity
    from django.db.models import F
    opps = Opportunity.objects.filter(corporate_id=cid, stage__is_won=False, stage__is_lost=False)
    month = request.GET.get("month")
    if month:
        opps = opps.filter(expected_close_date__startswith=month)
    total_pipeline = opps.aggregate(t=Sum("expected_revenue"))["t"] or Decimal("0")
    weighted = sum(o.weighted_revenue for o in opps)
    return Response({
        "total_pipeline_value": str(total_pipeline),
        "weighted_forecast": str(weighted),
        "opportunity_count": opps.count(),
    })

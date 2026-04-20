"""
CRM Product Catalog Sync Views
Handles product synchronization from Inventory Service
"""
import logging
from decimal import Decimal
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from crm_service.crm.models.product_catalog import ProductCatalogItem

logger = logging.getLogger(__name__)


@api_view(['POST'])
def sync_product_catalog(request):
    """
    Sync product to CRM catalog from inventory
    
    POST /api/crm/product-catalog/sync/
    
    Expected payload:
    {
        "product_id": "uuid",
        "operation": "create|update|delete",
        "product_name": "Product Name",
        "description": "Description",
        "list_price": "99.99",
        "category": "Electronics",
        "is_active": true
    }
    """
    try:
        data = request.data
        corporate_id = request.corporate_id
        
        # Validate required fields
        if not data.get('product_id'):
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not data.get('operation'):
            return Response(
                {'error': 'operation is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        operation = data['operation']
        product_id = data['product_id']
        
        if operation == 'create':
            # Check if already exists
            if ProductCatalogItem.objects.filter(
                product_id=product_id,
                corporate_id=corporate_id
            ).exists():
                return Response(
                    {'message': 'Product already exists in catalog'},
                    status=status.HTTP_200_OK
                )
            
            # Create catalog item
            item = ProductCatalogItem.objects.create(
                product_id=product_id,
                name=data.get('product_name', 'Unnamed Product'),
                description=data.get('description', ''),
                list_price=Decimal(str(data.get('list_price', '0.00'))),
                category=data.get('category', ''),
                is_active=data.get('is_active', True),
                is_available_for_sale=data.get('is_active', True),
                corporate_id=corporate_id,
                synced_from_inventory=True
            )
            
            logger.info(f"Created CRM catalog item {item.id} from inventory sync")
            
            return Response({
                'id': str(item.id),
                'product_id': str(item.product_id),
                'name': item.name,
                'message': 'Product added to catalog successfully'
            }, status=status.HTTP_201_CREATED)
            
        elif operation == 'update':
            # Get existing item
            try:
                item = ProductCatalogItem.objects.get(
                    product_id=product_id,
                    corporate_id=corporate_id
                )
            except ProductCatalogItem.DoesNotExist:
                # Create if doesn't exist
                item = ProductCatalogItem.objects.create(
                    product_id=product_id,
                    name=data.get('product_name', 'Unnamed Product'),
                    description=data.get('description', ''),
                    list_price=Decimal(str(data.get('list_price', '0.00'))),
                    category=data.get('category', ''),
                    is_active=data.get('is_active', True),
                    is_available_for_sale=data.get('is_active', True),
                    corporate_id=corporate_id,
                    synced_from_inventory=True
                )
                
                logger.info(f"Created CRM catalog item {item.id} (update operation)")
                
                return Response({
                    'id': str(item.id),
                    'product_id': str(item.product_id),
                    'name': item.name,
                    'message': 'Product added to catalog successfully'
                }, status=status.HTTP_201_CREATED)
            
            # Update fields
            if 'product_name' in data:
                item.name = data['product_name']
            if 'description' in data:
                item.description = data['description']
            if 'list_price' in data:
                item.list_price = Decimal(str(data['list_price']))
            if 'category' in data:
                item.category = data['category']
            if 'is_active' in data:
                item.is_active = data['is_active']
                item.is_available_for_sale = data['is_active']
            
            item.save()
            
            logger.info(f"Updated CRM catalog item {item.id} from inventory sync")
            
            return Response({
                'id': str(item.id),
                'product_id': str(item.product_id),
                'name': item.name,
                'message': 'Product catalog updated successfully'
            }, status=status.HTTP_200_OK)
            
        elif operation == 'delete':
            # Soft delete - mark as inactive
            try:
                item = ProductCatalogItem.objects.get(
                    product_id=product_id,
                    corporate_id=corporate_id
                )
                item.is_active = False
                item.is_available_for_sale = False
                item.save(update_fields=['is_active', 'is_available_for_sale', 'updated_at'])
                
                logger.info(f"Deleted (deactivated) CRM catalog item {item.id}")
                
                return Response({
                    'message': 'Product removed from catalog successfully'
                }, status=status.HTTP_200_OK)
            except ProductCatalogItem.DoesNotExist:
                return Response({
                    'message': 'Product not found in catalog'
                }, status=status.HTTP_200_OK)
        
        else:
            return Response(
                {'error': f'Invalid operation: {operation}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except Exception as e:
        logger.error(f"Error syncing product to CRM catalog: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to sync product: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_catalog(request):
    """
    List all products in CRM catalog
    
    GET /api/crm/product-catalog/
    """
    try:
        corporate_id = request.corporate_id
        
        items = ProductCatalogItem.objects.filter(
            corporate_id=corporate_id,
            is_active=True,
            is_available_for_sale=True
        ).order_by('name')
        
        data = [{
            'id': str(item.id),
            'product_id': str(item.product_id),
            'name': item.name,
            'description': item.description,
            'list_price': str(item.list_price),
            'category': item.category,
            'is_active': item.is_active,
        } for item in items]
        
        return Response({
            'count': len(data),
            'products': data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing CRM catalog: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Failed to list catalog: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

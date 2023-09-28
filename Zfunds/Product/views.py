from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from drf_spectacular.utils import extend_schema
from Zfunds.Accounts.models import CustomUser

from .models import Product, Category, Order
from .serializers import ProductSerializer, CategorySerializer

class ProductView(APIView):
    """
    ViewSet for viewing and creating Products
    """
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses=ProductSerializer)
    def get(self, request, format=None):
        queryset = Product.objects.all()
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(responses=ProductSerializer)
    def post(self, request, format=None):
        if 'category' in request.data:
            category = None
            category_name = request.data['category']
            try:
                category = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                category_serializer = CategorySerializer(data={'name': category_name})

                if category_serializer.is_valid():
                    category_serializer.save()
                    category = category_serializer.instance
                else:
                    return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Attach the category to the request data
            request.data['category'] = category.id

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['category'] = category
            serializer.save()
            resp = dict(serializer.data)
            resp.pop("description")
            return Response(resp, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseProductView(APIView):
    def post(self, request):
        advisor = request.user  # Assuming the advisor is the authenticated user
        client_id = request.data.get('client_id')
        product_id = request.data.get('product_id')

        try:
            client = CustomUser.objects.get(id=client_id, client_advisor=advisor)
            product = Product.objects.get(id=product_id)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create an order record
        order = Order.objects.create(advisor=advisor, client=client, product=product)

        # You can save the purchase details or send the unique link to the client as needed

        return Response({'message': 'Product purchased successfully', 'order_id': order.id}, status=status.HTTP_201_CREATED)
 
    
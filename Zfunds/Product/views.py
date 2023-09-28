from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from drf_spectacular.utils import extend_schema
from Zfunds.Accounts.models import CustomUser, Advisor
from rest_framework.authentication import TokenAuthentication

from .models import Product, Category, Order
from .serializers import ProductSerializer, CategorySerializer

class ProductView(APIView):
    """
    View for viewing and creating Products by Admin
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
    """
        View for Purchasing Products
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_unique_link(self, request, product, order, user):
        host = request.get_host()

        unique_link = f"{host}/purchase-details/{product.id}{order.id}{user.id}"
        return unique_link

    def post(self, request):
        user = request.user 

        # if the user is advisor then request data should contain client name, mobile, and product id
        product_id = request.data.get('product_id')
        client_name = request.data.get('name')
        client_mobile = request.data.get('mobile')

        try:
            adv = Advisor.objects.get(user_profile=user)
            client = CustomUser.objects.get(mobile=client_mobile, client_advisor=adv)
            product = Product.objects.get(id=product_id)
        except CustomUser.DoesNotExist:
            return Response({'message': 'Client not found'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create an order record
        order = Order.objects.create(advisor=adv, client=client, product=product)
        unique_link = self.get_unique_link(request, product, order, user)
        order.unique_link = unique_link
        order.save()
        msg = "Product purchased successfully"
        
        if(user.is_advisor):
            msg = "Product purchased successfully for client"

        return Response({'message': msg, 'unique_link': unique_link}, status=status.HTTP_201_CREATED)
 
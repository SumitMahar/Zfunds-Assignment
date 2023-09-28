from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from drf_spectacular.utils import extend_schema

from .models import Product, Category
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

    
    
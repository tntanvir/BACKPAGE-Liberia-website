from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import Product, ProductImage, ProductCategory, CartItem, Property, PropertyImage, PropertyCartItem
from .serializers import ProductSerializer, ProductCategorySerializer, CartItemSerializer, CartItemUpdateSerializer, PropertySerializer, PropertyImageSerializer, PropertyCartItemSerializer
from rest_framework import permissions


class ProductCategoryListAPIView(APIView):
    def get(self, request):
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data)

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 1000

class ProductListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get(self, request):
        products = Product.objects.all()
        category_name = request.query_params.get('category')
        if category_name:
            products = products.filter(category__name__iexact=category_name)
        
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save(user=request.user)

            # ✅ THIS IS THE KEY LINE
            images = request.FILES.getlist('images')

            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image
                )

            return Response(
                ProductSerializer(product).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return None

    def get(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def patch(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Ensure only the owner can update
        if product.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            product = serializer.save()

            #  ADD MORE IMAGES
            images = request.FILES.getlist('images')
            for image in images:
                ProductImage.objects.create(
                    product=product,
                    image=image
                )

            return Response(ProductSerializer(product).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        if not product:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Ensure only the owner can delete
        if product.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class TopSellProductListAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TodayPickProduct(APIView):
    def get(self, request):
        products = Product.objects.all()
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class RecommendedProduct(APIView):
    def get(self, request):
        products = Product.objects.all()
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class UserProductListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.filter(user=request.user)
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class CartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart_items = CartItem.objects.filter(user=request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            quantity = serializer.validated_data['quantity']
            
            cart_item, created = CartItem.objects.get_or_create(
                user=request.user, 
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CartDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return CartItem.objects.get(pk=pk, user=user)
        except CartItem.DoesNotExist:
            return None

    def patch(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CartItemUpdateSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PropertyListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get(self, request):
        properties = Property.objects.all()
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(properties, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PropertySerializer(data=request.data)
        if serializer.is_valid():
            property_obj = serializer.save(user=request.user)

            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(
                    property=property_obj,
                    image=image
                )

            return Response(PropertySerializer(property_obj).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PropertyDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_object(self, pk):
        try:
            return Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            return None

    def get(self, request, pk):
        property_obj = self.get_object(pk)
        if not property_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PropertySerializer(property_obj)
        return Response(serializer.data)

    def patch(self, request, pk):
        property_obj = self.get_object(pk)
        if not property_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        # Ensure only the owner can update
        if property_obj.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = PropertySerializer(property_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        property_obj = self.get_object(pk)
        if not property_obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        # Ensure only the owner can delete
        if property_obj.user != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        property_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPropertyListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        properties = Property.objects.filter(user=request.user)
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(properties, request)
        serializer = PropertySerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class PropertyCartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart_items = PropertyCartItem.objects.filter(user=request.user)
        serializer = PropertyCartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PropertyCartItemSerializer(data=request.data)
        if serializer.is_valid():
            property_obj = serializer.validated_data['property']
            # quantity = serializer.validated_data['quantity']
            
            cart_item, created = PropertyCartItem.objects.get_or_create(
                user=request.user, 
                property=property_obj,
                # defaults={'quantity': quantity}
            )
            
            if not created:
                # cart_item.quantity += quantity
                cart_item.save()
            
            return Response(PropertyCartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertyCartDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return PropertyCartItem.objects.get(pk=pk, user=user)
        except PropertyCartItem.DoesNotExist:
            return None

    def get(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PropertyCartItemSerializer(cart_item)
        return Response(serializer.data)

    def patch(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PropertyCartItemSerializer(cart_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        if not cart_item:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
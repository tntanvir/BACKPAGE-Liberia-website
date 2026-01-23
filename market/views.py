from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, parsers
from .models import Product, ProductImage, ProductCategory
from .serializers import ProductSerializer, ProductCategorySerializer


class ProductCategoryListAPIView(APIView):
    def get(self, request):
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response(serializer.data)

class ProductListCreateAPIView(APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get(self, request):
        products = Product.objects.all()
        category_name = request.query_params.get('category')
        if category_name:
            products = products.filter(category__name__iexact=category_name)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)

        if serializer.is_valid():
            product = serializer.save()

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

        serializer = ProductSerializer(
            product,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            product = serializer.save()

            # ✅ ADD MORE IMAGES
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

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.urls import path
from .views import ProductListCreateAPIView, ProductDetailAPIView, ProductCategoryListAPIView

urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('product-categories/', ProductCategoryListAPIView.as_view(), name='product-category-list'),
]

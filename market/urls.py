from django.urls import path
from .views import (
    ProductListCreateAPIView, ProductDetailAPIView, ProductCategoryListAPIView, 
    RecommendedProduct, TodayPickProduct, TopSellProductListAPIView, 
    CartAPIView, CartDetailAPIView, UserProductListAPIView,
    PropertyListCreateAPIView, PropertyDetailAPIView, UserPropertyListAPIView,
    PropertyCartAPIView, PropertyCartDetailAPIView
)

urlpatterns = [
    path('products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('my-products/', UserProductListAPIView.as_view(), name='user-product-list'),
    
    path('products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),
    path('product-categories/', ProductCategoryListAPIView.as_view(), name='product-category-list'),

    path('properties/', PropertyListCreateAPIView.as_view(), name='property-list-create'),
    path('properties/<int:pk>/', PropertyDetailAPIView.as_view(), name='property-detail'),
    path('my-properties/', UserPropertyListAPIView.as_view(), name='user-property-list'),

    path('property-cart/', PropertyCartAPIView.as_view(), name='property-cart'),
    path('property-cart/<int:pk>/', PropertyCartDetailAPIView.as_view(), name='property-cart-detail'),

    path('cart/', CartAPIView.as_view(), name='cart'),
    path('cart/<int:pk>/', CartDetailAPIView.as_view(), name='cart-detail'),

    path('recommended-products/', RecommendedProduct.as_view(), name='recommended-product-list'),
    path('today-pick-products/', TodayPickProduct.as_view(), name='today-pick-product-list'),
    path('top-sell-products/', TopSellProductListAPIView.as_view(), name='top-sell-product-list'),
]

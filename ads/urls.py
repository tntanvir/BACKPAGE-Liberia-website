from django.urls import path
from .views import AdsListView, AdsPageView

urlpatterns = [
    path('', AdsListView.as_view(), name='ads-list'),
    path('pages/', AdsPageView.as_view(), name='ads-page-list'),
]

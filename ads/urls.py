from django.urls import path
from .views import AdsListView

urlpatterns = [
    path('', AdsListView.as_view(), name='ads-list'),
]

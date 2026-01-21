from django.urls import path
from . import views

urlpatterns = [
    path('videos/', views.VideoListCreateView.as_view(), name='video-list-create'),
    path('videos/<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    path('query-video/', views.AnalyzeView.as_view(), name='analyze'),
    path('download/', views.DownloadView.as_view(), name='download'),
    path('status/<str:task_id>/', views.TaskStatusView.as_view(), name='task_status'),
    path('retrieve/<str:task_id>/', views.FileRetrieveView.as_view(), name='file_retrieve'),
]

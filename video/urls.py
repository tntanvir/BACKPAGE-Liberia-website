from django.urls import path
from . import views

urlpatterns = [
    path('videos/', views.VideoListCreateView.as_view(), name='video-list-create'),
    path('videos/<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    path('query-video/', views.AnalyzeView.as_view(), name='analyze'),
    path('download/', views.DownloadView.as_view(), name='download'),
    path('status/<str:task_id>/', views.TaskStatusView.as_view(), name='task_status'),
    path('retrieve/<str:task_id>/', views.FileRetrieveView.as_view(), name='file_retrieve'),
    
    # New Endpoints
    path('music-videos/', views.MusicVideoListView.as_view(), name='music-video-list'),
    path('movies/', views.MovieListView.as_view(), name='movie-list'),
    path('trending/', views.TrendingVideoListView.as_view(), name='trending-video-list'),
    path('categories/', views.VideoCategoryListView.as_view(), name='video-category-list'),
    path('view/', views.VideoViewCreateView.as_view(), name='video-view-create'),
]

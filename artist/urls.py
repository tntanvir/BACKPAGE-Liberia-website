from django.urls import path
from . import views

urlpatterns = [
    path('artists/', views.ArtistListCreateView.as_view(), name='artist-list-create'),
    path('most-popular/artists/', views.PopularArtistView.as_view(), name='artist-most-popular'),
    path('featured/artists/', views.FeaturedArtistView.as_view(), name='artist-featured'),
    path('artists/<int:pk>/', views.ArtistListCreateView.as_view(), name='artist-detail'),
    
    path('music/', views.MusicListCreateView.as_view(), name='music-list-create'),
    path('music/<int:pk>/', views.MusicListCreateView.as_view(), name='music-detail'),
    path('trending/music/', views.TrendingMusicView.as_view(), name='music-trending'),
    path('music/latest/', views.LatestMusicByArtistView.as_view(), name='music-latest'),
    
    path('likes/<int:music_pk>/', views.LikeCreateView.as_view(), name='like-create'),
    path('dislikes/<int:music_pk>/', views.DislikeCreateView.as_view(), name='dislike-create'),
    
    path('comments/<int:music_pk>/', views.CommentListView.as_view(), name='comment-list-create'),

    path('my-profile-data/', views.MyProfileDataView.as_view(), name='my-profile-data')

]

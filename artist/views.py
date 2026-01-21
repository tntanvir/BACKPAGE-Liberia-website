from rest_framework import status, permissions
from rest_framework.response import Response
from django.db.models import Count, F
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Artist, Music, Like, Dislike, Comment , CommentLike , Listen , Download
from django.db.models import Count, Sum, Subquery, OuterRef, IntegerField, Max
from django.db.models.functions import Coalesce
from .serializers import (
    ArtistSerializer,
    MusicSerializer,
    LikeSerializer,
    DislikeSerializer,
    CommentSerializer,

)
from rest_framework.pagination import PageNumberPagination



class ArtistPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class ArtistListCreateView(APIView):
    
    def get_object(self, pk):
        return get_object_or_404(Artist, pk=pk)

    def get(self, request, pk=None):
        # Retrieve single artist
        if pk is not None:
            artist = self.get_object(pk)
            serializer = ArtistSerializer(artist)
            return Response(serializer.data)

        # List artists with optional filtering
        artists = Artist.objects.all()
        artist_type = request.query_params.get('artist_type')

        if artist_type:
            artists = artists.filter(artist_type=artist_type)

        paginator = ArtistPagination()
        result_page = paginator.paginate_queryset(artists, request)
        serializer = ArtistSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        if not pk:
             return Response({'error': 'Method PUT not allowed on collection'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        artist = self.get_object(pk)
        serializer = ArtistSerializer(artist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
             return Response({'error': 'Method DELETE not allowed on collection'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        artist = self.get_object(pk)
        artist.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class MusicPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100
class MusicListCreateView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        # Retrieve single music item
        if pk is not None:
            music = get_object_or_404(Music, pk=pk)
            serializer = MusicSerializer(music)
            return Response(serializer.data)

        # List view with optional filtering
        queryset = Music.objects.all()
        artist_id = request.query_params.get('artist')
        music_search = request.query_params.get('search')
        
        if artist_id:
            queryset = queryset.filter(artist_id=artist_id)

        if music_search:
            queryset = queryset.filter(title__icontains=music_search)

        paginator = MusicPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = MusicSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # def post(self, request):
    #     serializer = MusicSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    


class LikeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, music_pk=None):
        try:
            music = Music.objects.get(pk=music_pk)
        except Music.DoesNotExist:
            return Response({'error': 'Music not found'}, status=status.HTTP_404_NOT_FOUND)
        like = Like.objects.filter(user=request.user, music=music)
        like_count = Like.objects.filter(music=music).count()
        if like.exists():
            like.delete()
            return Response({'message': 'Like removed','like_count': like_count-1}, status=status.HTTP_200_OK)
        like = Like.objects.create(user=request.user, music=music)
        return Response({'message': 'Like added','like_count': like_count+1}, status=status.HTTP_201_CREATED)

class DislikeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, music_pk=None):
        try:
            music = Music.objects.get(pk=music_pk)
        except Music.DoesNotExist:
            return Response({'error': 'Music not found'}, status=status.HTTP_404_NOT_FOUND)
        dislike = Dislike.objects.filter(user=request.user, music=music)
        dislike_count = Dislike.objects.filter(music=music).count()
        if dislike.exists():
            dislike.delete()
            return Response({'message': 'Dislike removed','dislike_count': dislike_count-1}, status=status.HTTP_200_OK)
        dislike = Dislike.objects.create(user=request.user, music=music)
        return Response({'message': 'Dislike added','dislike_count': dislike_count+1}, status=status.HTTP_201_CREATED)


class CommentListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, music_pk=None):
        try:
            music = Music.objects.get(pk=music_pk)
        except Music.DoesNotExist:
            return Response({'error': 'Music not found'}, status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(music=music)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, music_pk=None):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
            
        data = request.data.copy()
        if music_pk:
            data['music'] = music_pk
            
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CommentLikeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, comment_pk=None):
        try:
            comment = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
        comment_like = CommentLike.objects.filter(user=request.user, comment=comment)
        comment_like_count = CommentLike.objects.filter(comment=comment).count()
        if comment_like.exists():
            comment_like.delete()
            return Response({'message': 'Comment like removed','comment_like_count': comment_like_count-1}, status=status.HTTP_200_OK)
        comment_like = CommentLike.objects.create(user=request.user, comment=comment)
        return Response({'message': 'Comment like added','comment_like_count': comment_like_count+1}, status=status.HTTP_201_CREATED)



class FeaturedArtistView(APIView):
    def get(self, request):
        # Featured আর্টিস্টদের লাইক-ডিসলাইক ক্যালকুলেট করে সর্টিং এবং টপ ২০ স্লাইসিং
        artists = Artist.objects.annotate(
            total_likes=Count('music__like', distinct=True),
            total_dislikes=Count('music__dislike', distinct=True),
            featured_score=F('total_likes') - F('total_dislikes')
        ).order_by('-featured_score', '-total_likes')[:20]  # এখানে [:20] টপ ২০ জন দেখাবে

        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)



class PopularArtistView(APIView):
    def get(self, request):
        artists = Artist.objects.annotate(
            t_likes=Count('music__like', distinct=True),
            t_comments=Count('music__comment', distinct=True),
            t_downloads=Count('music__download', distinct=True),
            t_listens=Count('music__listen', distinct=True),
            t_dislikes=Count('music__dislike', distinct=True),
            
            # ওভারঅল ভ্যালু ক্যালকুলেশন
            overall_score=(
                F('t_likes') + F('t_comments') + F('t_downloads') + F('t_listens')
            ) - F('t_dislikes')
        ).order_by('-overall_score')[:20]  # টপ ২০ জন জনপ্রিয় আর্টিস্ট

        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)

class MyProfileDataView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        like = Like.objects.filter(user=request.user).count()
        dislike = Dislike.objects.filter(user=request.user).count()
        comment = Comment.objects.filter(user=request.user).count()
        listen = Listen.objects.filter(user=request.user).count()
        download = Download.objects.filter(user=request.user).count()

        return Response({
            'like': like,
            'dislike': dislike,
            'comment': comment,
            'listen': listen,
            'download': download,
        })
        
        


class TrendingMusicView(APIView):
    def get(self, request):
        perams = request.query_params.get('perams')
        musics = Music.objects.filter(music_type=perams).annotate(
            total_likes=Count('like', distinct=True),
            total_dislikes=Count('dislike', distinct=True),
            total_comments=Count('comment', distinct=True),
            calc_total_downloads=Count('download', distinct=True),
            calc_total_listens=Count('listen', distinct=True),
            overall_score=(
                F('total_likes') + F('total_comments') + F('calc_total_downloads') + F('calc_total_listens')
            ) - F('total_dislikes')
        ).order_by('-overall_score')

        serializer = MusicSerializer(musics, many=True)
        return Response(serializer.data)






class LatestMusicByArtistView(APIView):
    def get(self, request):
        # Fetch artists ordered by their latest music creation date
        latest_artists = Artist.objects.annotate(
            latest_release=Max('music__created_at')
        ).filter(latest_release__isnull=False).order_by('-latest_release')[:20]
        
        serializer = ArtistSerializer(latest_artists, many=True)
        return Response(serializer.data)













# class MostPopularArtistView(APIView):

#     def get(self, request):

#         # --- Music aggregates ---
#         music_listen_subquery = (
#             Music.objects
#             .filter(artist=OuterRef('pk'))
#             .values('artist')
#             .annotate(total=Sum('total_listens'))
#             .values('total')
#         )

#         music_download_subquery = (
#             Music.objects
#             .filter(artist=OuterRef('pk'))
#             .values('artist')
#             .annotate(total=Sum('total_downloads'))
#             .values('total')
#         )

#         music_count_subquery = (
#             Music.objects
#             .filter(artist=OuterRef('pk'))
#             .values('artist')
#             .annotate(total=Count('id'))
#             .values('total')
#         )

#         # --- Likes via Music ---
#         like_subquery = (
#             Like.objects
#             .filter(music__artist=OuterRef('pk'))
#             .values('music__artist')
#             .annotate(total=Count('id'))
#             .values('total')
#         )

#         artists = (
#             Artist.objects
#             .annotate(
#                 calculated_total_listens=Coalesce(
#                     Subquery(music_listen_subquery, output_field=IntegerField()), 0
#                 ),
#                 calculated_total_downloads=Coalesce(
#                     Subquery(music_download_subquery, output_field=IntegerField()), 0
#                 ),
#                 calculated_total_music=Coalesce(
#                     Subquery(music_count_subquery, output_field=IntegerField()), 0
#                 ),
#                 calculated_total_likes=Coalesce(
#                     Subquery(like_subquery, output_field=IntegerField()), 0
#                 ),
#             )
#             .order_by(
#                 '-calculated_total_listens',
#                 '-calculated_total_downloads',
#                 '-calculated_total_likes',
#                 '-calculated_total_music',
#             )
#         )

#         serializer = ArtistSerializer(artists, many=True)
#         return Response(serializer.data)

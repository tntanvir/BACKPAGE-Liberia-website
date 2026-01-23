from rest_framework import serializers
from .models import Artist, Music, Like, Dislike, Comment, Download , Listen , Category , CommentLike
from django.db.models import Sum, Count
from authsystem.serializers import UserSerializer

class ArtistSerializer(serializers.ModelSerializer):
    total_music = serializers.SerializerMethodField()
    total_listens = serializers.SerializerMethodField()
    total_downloads = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    total_dislikes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = [
            'id',
            'image',
            'name',
            'artist_type',
            'bio',
            'location',
            'total_music',
            'total_listens',
            'total_downloads',
            'total_likes',
            'total_dislikes',
            'total_comments',
            'created_at',
        ]

    def get_total_music(self, obj):
        return Music.objects.filter(artist=obj).count()

    def get_total_listens(self, obj):
        # return Music.objects.filter(artist=obj).aggregate(total=Sum('total_listens'))['total'] or 0
        return Listen.objects.filter(music__artist=obj).count()
    
    def get_total_downloads(self, obj):
        # return Music.objects.filter(artist=obj).aggregate(total=Sum('total_downloads'))['total'] or 0
        return Download.objects.filter(music__artist=obj).count()
    
    def get_total_likes(self, obj):
        return Like.objects.filter(music__artist=obj).count()
    
    def get_total_dislikes(self, obj):
        return Dislike.objects.filter(music__artist=obj).count()
    
    def get_total_comments(self, obj):
        return Comment.objects.filter(music__artist=obj).count()



class MusicSerializer(serializers.ModelSerializer):
    total_likes = serializers.SerializerMethodField()
    total_dislikes = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    artist = serializers.PrimaryKeyRelatedField(
        queryset=Artist.objects.all(), write_only=True
    )
    artist_detail = ArtistSerializer(source='artist', read_only=True)
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.music_type:
            representation['music_type'] = instance.music_type.name
        return representation
    
    class Meta:
        model = Music
        fields = [
            'id',
            'artist',
            'artist_detail',
            'image',
            'audio',
            'title',
            'music_type',
            'description',
            'total_listens',
            'total_downloads',
            'total_likes',
            'total_dislikes',
            'total_comments',
            'created_at',
        ]

    def get_total_likes(self, obj):
        return Like.objects.filter(music=obj).count()

    def get_total_dislikes(self, obj):
        return Dislike.objects.filter(music=obj).count()

    def get_total_comments(self, obj):
        return Comment.objects.filter(music=obj).count()

    def get_total_downloads(self, obj):
        return Download.objects.filter(music=obj).count()
    
    def get_total_listens(self, obj):
        return Listen.objects.filter(music=obj).count()
    

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['user']

class DislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dislike
        fields = '__all__'
        read_only_fields = ['user']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    like = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['user']

    def get_like(self, obj):
        return CommentLike.objects.filter(comment=obj).count()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
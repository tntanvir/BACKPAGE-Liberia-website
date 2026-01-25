from rest_framework import serializers
from .models import Video, VideoCategory, Videoview

class VideoCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoCategory
        fields = '__all__'

    def __str__(self):
        return self.name

class VideoSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Video
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.youtube_url:
            representation.pop('menual_video', None)
        elif instance.menual_video:
            representation.pop('youtube_url', None)
        return representation

class VideoviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videoview
        fields = ['video', 'view_count']
        read_only_fields = ['view_count']

class AnalyzeSerializer(serializers.Serializer):
   url = serializers.URLField(required=True)


class DownloadSerializer(serializers.Serializer):
   url = serializers.URLField(required=True)
   format_id = serializers.CharField(required=True)
   music_id = serializers.IntegerField(required=False, allow_null=True)
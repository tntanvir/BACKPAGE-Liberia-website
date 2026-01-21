from rest_framework import serializers
from .models import Video

class VideoSerializer(serializers.ModelSerializer):
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

class AnalyzeSerializer(serializers.Serializer):
   url = serializers.URLField(required=True)


class DownloadSerializer(serializers.Serializer):
   url = serializers.URLField(required=True)
   format_id = serializers.CharField(required=True)
   music_id = serializers.IntegerField(required=False, allow_null=True)
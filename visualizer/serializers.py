from rest_framework import serializers
from .models import (
    OllamaConfiguration,
    UploadedFile,
    Conversation,
    Message,
    Visualization,
    ProcessingJob
)


class OllamaConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OllamaConfiguration
        fields = [
            'id', 'model_name', 'base_url', 'port', 'is_active',
            'is_available', 'parameters', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = [
            'id', 'file', 'file_name', 'file_type', 'file_size',
            'parsed_data', 'upload_date', 'session_id'
        ]
        read_only_fields = ['upload_date', 'parsed_data']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'message_type', 'content',
            'metadata', 'created_at'
        ]
        read_only_fields = ['created_at']


class VisualizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visualization
        fields = [
            'id', 'conversation', 'message', 'title', 'chart_type',
            'chart_config', 'explanation', 'created_at'
        ]
        read_only_fields = ['created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    visualizations = VisualizationSerializer(many=True, read_only=True)
    ollama_model_name = serializers.CharField(source='ollama_model.model_name', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'session_id', 'created_at', 'updated_at',
            'ollama_model', 'ollama_model_name', 'messages', 'visualizations'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProcessingJobSerializer(serializers.ModelSerializer):
    elapsed_time = serializers.SerializerMethodField()

    class Meta:
        model = ProcessingJob
        fields = [
            'id', 'job_id', 'conversation', 'status', 'progress',
            'estimated_time', 'elapsed_time', 'error_message', 'result',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'started_at', 'completed_at', 'elapsed_time']

    def get_elapsed_time(self, obj):
        return obj.get_elapsed_time()


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)
    session_id = serializers.CharField(required=True)
    file_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=list
    )


class FileUploadResponseSerializer(serializers.Serializer):
    file_id = serializers.IntegerField()
    file_name = serializers.CharField()
    file_type = serializers.CharField()
    file_size = serializers.IntegerField()
    parsed = serializers.BooleanField()

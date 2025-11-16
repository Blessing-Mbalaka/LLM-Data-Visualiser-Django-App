from django.contrib import admin
from .models import (
    OllamaConfiguration,
    UploadedFile,
    Conversation,
    Message,
    Visualization,
    ProcessingJob
)


@admin.register(OllamaConfiguration)
class OllamaConfigurationAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'base_url', 'port', 'is_active', 'is_available', 'updated_at']
    list_filter = ['is_active', 'is_available']
    search_fields = ['model_name']


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'file_size', 'upload_date', 'session_id']
    list_filter = ['file_type', 'upload_date']
    search_fields = ['file_name', 'session_id']


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'ollama_model', 'created_at', 'updated_at']
    list_filter = ['created_at', 'ollama_model']
    search_fields = ['session_id']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'message_type', 'content_preview', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['content']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content


@admin.register(Visualization)
class VisualizationAdmin(admin.ModelAdmin):
    list_display = ['title', 'chart_type', 'conversation', 'created_at']
    list_filter = ['chart_type', 'created_at']
    search_fields = ['title', 'explanation']


@admin.register(ProcessingJob)
class ProcessingJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'status', 'progress', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['job_id']

from django.db import models
from django.utils import timezone
import json


class OllamaConfiguration(models.Model):
    """Store Ollama model configurations"""
    model_name = models.CharField(max_length=255, unique=True)
    base_url = models.URLField(default='http://localhost:11434')
    port = models.IntegerField(default=11434)
    is_active = models.BooleanField(default=False)
    is_available = models.BooleanField(default=False)
    parameters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_active', '-updated_at']

    def __str__(self):
        return f"{self.model_name} ({'Active' if self.is_active else 'Inactive'})"


class UploadedFile(models.Model):
    """Store uploaded data files"""
    FILE_TYPES = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('yaml', 'YAML'),
        ('xlsx', 'Excel'),
        ('pdf', 'PDF'),
    ]

    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    file_size = models.IntegerField()  # in bytes
    parsed_data = models.JSONField(null=True, blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=255, db_index=True)

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"{self.file_name} ({self.get_file_type_display()})"


class Conversation(models.Model):
    """Store chat conversations"""
    session_id = models.CharField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ollama_model = models.ForeignKey(
        OllamaConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation {self.session_id[:8]}... ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class Message(models.Model):
    """Store individual messages in conversations"""
    MESSAGE_TYPES = [
        ('user', 'User'),
        ('ai', 'AI'),
        ('system', 'System'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."


class Visualization(models.Model):
    """Store generated visualizations"""
    CHART_TYPES = [
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart'),
        ('radar', 'Radar Chart'),
        ('polarArea', 'Polar Area Chart'),
        ('scatter', 'Scatter Plot'),
        ('bubble', 'Bubble Chart'),
    ]

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='visualizations'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='visualizations',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES)
    chart_config = models.JSONField()  # Full Chart.js configuration
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_chart_type_display()})"


class ProcessingJob(models.Model):
    """Track long-running processing jobs"""
    JOB_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    job_id = models.CharField(max_length=255, unique=True, db_index=True)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='jobs'
    )
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='pending')
    progress = models.IntegerField(default=0)  # 0-100
    estimated_time = models.IntegerField(null=True, blank=True)  # seconds
    error_message = models.TextField(blank=True)
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.job_id[:8]}... ({self.get_status_display()})"

    def get_elapsed_time(self):
        """Calculate elapsed time in seconds"""
        if self.started_at:
            end_time = self.completed_at or timezone.now()
            return (end_time - self.started_at).total_seconds()
        return 0

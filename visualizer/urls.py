from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OllamaConfigurationViewSet,
    FileUploadViewSet,
    ConversationViewSet,
    ProcessingJobViewSet,
    health_check
)

router = DefaultRouter()
router.register(r'ollama', OllamaConfigurationViewSet, basename='ollama')
router.register(r'files', FileUploadViewSet, basename='files')
router.register(r'conversations', ConversationViewSet, basename='conversations')
router.register(r'jobs', ProcessingJobViewSet, basename='jobs')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health_check'),
]

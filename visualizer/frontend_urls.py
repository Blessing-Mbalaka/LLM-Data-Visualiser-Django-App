from django.urls import path
from .frontend_views import HomeView, OllamaConfigView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('ollama-config/', OllamaConfigView.as_view(), name='ollama_config'),
]

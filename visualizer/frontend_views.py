from django.shortcuts import render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'visualizer/index.html'


class OllamaConfigView(TemplateView):
    template_name = 'visualizer/ollama_config.html'

import requests
import json
from typing import Dict, List, Optional, Any
from django.conf import settings
from .models import OllamaConfiguration
import logging

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama API"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.timeout = 120  # 2 minutes timeout for LLM requests

    def check_connection(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection check failed: {str(e)}")
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """List all available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('models', [])
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []

    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=600,  # 10 minutes for model download
                stream=True
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {str(e)}")
            return False

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000
    ) -> Optional[str]:
        """Generate text using Ollama model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            return None

    def generate_with_json(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Optional[Dict]:
        """Generate structured JSON output from Ollama"""
        json_system_prompt = """You are a data visualization expert. You must respond ONLY with valid JSON.
Never include markdown code blocks, explanations, or any text outside the JSON structure.
Your response must be parseable by json.loads() in Python."""

        if system_prompt:
            json_system_prompt = f"{json_system_prompt}\n\n{system_prompt}"

        response_text = self.generate(
            model=model,
            prompt=prompt,
            system_prompt=json_system_prompt,
            temperature=0.3  # Lower temperature for more structured output
        )

        if not response_text:
            return None

        try:
            # Clean the response
            response_text = response_text.strip()
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                response_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else response_text
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}\nResponse: {response_text}")
            return None

    def auto_detect_and_configure(self) -> List[OllamaConfiguration]:
        """Auto-detect available Ollama models and configure them"""
        if not self.check_connection():
            logger.warning("Ollama server not available")
            return []

        models = self.list_models()
        configured_models = []

        for model_data in models:
            model_name = model_data.get('name', '')
            if not model_name:
                continue

            config, created = OllamaConfiguration.objects.get_or_create(
                model_name=model_name,
                defaults={
                    'base_url': self.base_url,
                    'port': 11434,
                    'is_available': True,
                    'parameters': {
                        'size': model_data.get('size', 0),
                        'modified_at': model_data.get('modified_at', ''),
                        'details': model_data.get('details', {})
                    }
                }
            )

            if not created:
                config.is_available = True
                config.parameters = {
                    'size': model_data.get('size', 0),
                    'modified_at': model_data.get('modified_at', ''),
                    'details': model_data.get('details', {})
                }
                config.save()

            configured_models.append(config)

        return configured_models

    def get_active_model(self) -> Optional[OllamaConfiguration]:
        """Get the currently active model configuration"""
        return OllamaConfiguration.objects.filter(is_active=True).first()

    def set_active_model(self, model_name: str) -> Optional[OllamaConfiguration]:
        """Set a model as active"""
        # Deactivate all models
        OllamaConfiguration.objects.update(is_active=False)
        
        # Activate the specified model
        try:
            config = OllamaConfiguration.objects.get(model_name=model_name)
            config.is_active = True
            config.save()
            return config
        except OllamaConfiguration.DoesNotExist:
            return None


class VisualizationGenerator:
    """Generate visualizations using LLM"""

    VISUALIZATION_PROMPT = """You are a data visualization expert. Analyze the provided data and create appropriate visualizations.

Data:
{data}

User Request: {user_request}

Create visualizations following these rules:

1. RESPONSE FORMAT - Respond with ONLY valid JSON (no markdown, no code blocks):
{{
  "explanation": "Brief explanation of the visualizations",
  "charts": [
    {{
      "type": "bar|line|pie|doughnut|radar|polarArea",
      "title": "Chart title",
      "data": {{
        "labels": ["Label1", "Label2", ...],
        "datasets": [
          {{
            "label": "Dataset name",
            "data": [value1, value2, ...],
            "backgroundColor": ["#color1", "#color2", ...],
            "borderColor": "#color",
            "borderWidth": 1
          }}
        ]
      }},
      "options": {{
        "responsive": true,
        "plugins": {{
          "title": {{"display": true, "text": "Chart Title"}},
          "legend": {{"display": true}}
        }}
      }}
    }}
  ]
}}

2. CHART TYPE SELECTION:
   - Use "bar" for comparisons, categorical data
   - Use "line" for trends over time
   - Use "pie" or "doughnut" for proportions/percentages
   - Use "radar" for multi-dimensional comparisons
   - Use "polarArea" for cyclical data

3. COLOR SCHEME: Use these gold/black theme colors:
   - Primary: #d4af37, #ffd700
   - Background: rgba(212, 175, 55, 0.6)
   - Border: #d4af37

4. DATA VALIDATION:
   - Ensure all data arrays have same length as labels
   - Use numeric values only in data arrays
   - Provide meaningful labels and titles

5. Create 1-3 visualizations based on data complexity
"""

    def __init__(self, ollama_service: OllamaService = None):
        self.ollama = ollama_service or OllamaService()

    def generate_visualizations(
        self,
        data: Dict[str, Any],
        user_request: str,
        model_name: Optional[str] = None
    ) -> Optional[Dict]:
        """Generate visualization configurations from data and user request"""
        
        if not model_name:
            active_model = self.ollama.get_active_model()
            if not active_model:
                logger.error("No active Ollama model found")
                return None
            model_name = active_model.model_name

        prompt = self.VISUALIZATION_PROMPT.format(
            data=json.dumps(data, indent=2),
            user_request=user_request
        )

        result = self.ollama.generate_with_json(
            model=model_name,
            prompt=prompt
        )

        return result

    def validate_chart_config(self, chart: Dict) -> bool:
        """Validate a chart configuration"""
        required_fields = ['type', 'title', 'data']
        
        if not all(field in chart for field in required_fields):
            return False

        valid_types = ['bar', 'line', 'pie', 'doughnut', 'radar', 'polarArea', 'scatter', 'bubble']
        if chart['type'] not in valid_types:
            return False

        data = chart.get('data', {})
        if 'labels' not in data or 'datasets' not in data:
            return False

        return True

from jsonschema import validate, ValidationError
import logging

logger = logging.getLogger(__name__)


# JSON Schema for Chart.js visualization configuration
CHART_CONFIG_SCHEMA = {
    "type": "object",
    "required": ["explanation", "charts"],
    "properties": {
        "explanation": {
            "type": "string",
            "minLength": 1
        },
        "charts": {
            "type": "array",
            "minItems": 1,
            "maxItems": 10,
            "items": {
                "type": "object",
                "required": ["type", "title", "data"],
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["bar", "line", "pie", "doughnut", "radar", "polarArea", "scatter", "bubble"]
                    },
                    "title": {
                        "type": "string",
                        "minLength": 1
                    },
                    "data": {
                        "type": "object",
                        "required": ["labels", "datasets"],
                        "properties": {
                            "labels": {
                                "type": "array",
                                "minItems": 1,
                                "items": {"type": ["string", "number"]}
                            },
                            "datasets": {
                                "type": "array",
                                "minItems": 1,
                                "items": {
                                    "type": "object",
                                    "required": ["label", "data"],
                                    "properties": {
                                        "label": {"type": "string"},
                                        "data": {
                                            "type": "array",
                                            "items": {"type": "number"}
                                        },
                                        "backgroundColor": {
                                            "oneOf": [
                                                {"type": "string"},
                                                {"type": "array", "items": {"type": "string"}}
                                            ]
                                        },
                                        "borderColor": {"type": "string"},
                                        "borderWidth": {"type": "number"}
                                    }
                                }
                            }
                        }
                    },
                    "options": {
                        "type": "object"
                    }
                }
            }
        }
    }
}


class VisualizationValidator:
    """Validate visualization configurations"""

    @staticmethod
    def validate_config(config: dict) -> tuple[bool, str]:
        """
        Validate visualization configuration against schema
        
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            validate(instance=config, schema=CHART_CONFIG_SCHEMA)
            
            # Additional validation rules
            for chart in config.get('charts', []):
                labels_length = len(chart['data']['labels'])
                
                for dataset in chart['data']['datasets']:
                    data_length = len(dataset['data'])
                    
                    if data_length != labels_length:
                        return False, f"Data length ({data_length}) doesn't match labels length ({labels_length}) in chart '{chart['title']}'"
                    
                    # Check for valid numeric data
                    if not all(isinstance(x, (int, float)) for x in dataset['data']):
                        return False, f"Invalid data values in chart '{chart['title']}' - must be numeric"
            
            return True, ""
            
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return False, str(e)
        except Exception as e:
            logger.error(f"Unexpected validation error: {str(e)}")
            return False, str(e)

    @staticmethod
    def fix_common_issues(config: dict) -> dict:
        """
        Attempt to fix common issues in visualization config
        """
        if not isinstance(config, dict):
            return config
            
        charts = config.get('charts', [])
        fixed_charts = []
        
        for chart in charts:
            if not isinstance(chart, dict):
                continue
                
            # Ensure required fields exist
            if 'type' not in chart or 'data' not in chart:
                continue
                
            # Set default title if missing
            if 'title' not in chart:
                chart['title'] = f"{chart['type'].title()} Chart"
            
            # Ensure data structure is correct
            data = chart.get('data', {})
            if 'labels' not in data or 'datasets' not in data:
                continue
                
            # Fix dataset issues
            datasets = data.get('datasets', [])
            fixed_datasets = []
            
            for dataset in datasets:
                if not isinstance(dataset, dict):
                    continue
                    
                # Ensure label exists
                if 'label' not in dataset:
                    dataset['label'] = 'Dataset'
                
                # Ensure data is array of numbers
                if 'data' in dataset and isinstance(dataset['data'], list):
                    # Try to convert to numbers
                    try:
                        dataset['data'] = [float(x) if x is not None else 0 for x in dataset['data']]
                    except:
                        continue
                    
                    # Ensure data length matches labels
                    labels_len = len(data.get('labels', []))
                    if len(dataset['data']) != labels_len:
                        # Truncate or pad data to match labels
                        if len(dataset['data']) > labels_len:
                            dataset['data'] = dataset['data'][:labels_len]
                        else:
                            dataset['data'] += [0] * (labels_len - len(dataset['data']))
                    
                    fixed_datasets.append(dataset)
            
            if fixed_datasets:
                data['datasets'] = fixed_datasets
                chart['data'] = data
                
                # Add default options if missing
                if 'options' not in chart:
                    chart['options'] = {
                        "responsive": True,
                        "plugins": {
                            "title": {"display": True, "text": chart['title']}
                        }
                    }
                
                fixed_charts.append(chart)
        
        config['charts'] = fixed_charts
        return config


def apply_visualization_rules(config: dict) -> dict:
    """
    Apply business rules and best practices to visualization config
    """
    if not isinstance(config, dict) or 'charts' not in config:
        return config
    
    for chart in config.get('charts', []):
        chart_type = chart.get('type', 'bar')
        
        # Apply color schemes based on chart type
        for dataset in chart.get('data', {}).get('datasets', []):
            if 'backgroundColor' not in dataset:
                # Use gold/black theme colors
                if chart_type in ['pie', 'doughnut']:
                    # Multiple colors for segments
                    colors = [
                        'rgba(212, 175, 55, 0.8)',
                        'rgba(255, 215, 0, 0.8)',
                        'rgba(212, 175, 55, 0.6)',
                        'rgba(255, 215, 0, 0.6)',
                        'rgba(212, 175, 55, 0.4)',
                        'rgba(255, 215, 0, 0.4)',
                    ]
                    num_items = len(dataset.get('data', []))
                    dataset['backgroundColor'] = (colors * ((num_items // len(colors)) + 1))[:num_items]
                else:
                    dataset['backgroundColor'] = 'rgba(212, 175, 55, 0.6)'
            
            if 'borderColor' not in dataset:
                dataset['borderColor'] = '#d4af37'
            
            if 'borderWidth' not in dataset:
                dataset['borderWidth'] = 2
        
        # Apply theme-specific options
        options = chart.get('options', {})
        
        if 'plugins' not in options:
            options['plugins'] = {}
        
        if 'title' not in options['plugins']:
            options['plugins']['title'] = {
                'display': True,
                'text': chart.get('title', 'Chart'),
                'color': '#d4af37',
                'font': {'size': 16, 'weight': '300'}
            }
        
        if 'legend' not in options['plugins']:
            options['plugins']['legend'] = {
                'display': True,
                'labels': {'color': '#ffffff', 'font': {'size': 12}}
            }
        
        chart['options'] = options
    
    return config

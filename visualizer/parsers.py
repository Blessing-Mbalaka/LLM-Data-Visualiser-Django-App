import pandas as pd
import json
import yaml
from typing import Dict, Any, List
from PyPDF2 import PdfReader
import logging

logger = logging.getLogger(__name__)


class FileParser:
    """Parse various file formats into structured data"""

    @staticmethod
    def parse_csv(file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV file"""
        try:
            df = pd.read_csv(file_path)
            # Convert to list of dictionaries
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"CSV parsing error: {str(e)}")
            raise

    @staticmethod
    def parse_excel(file_path: str) -> List[Dict[str, Any]]:
        """Parse Excel file"""
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Excel parsing error: {str(e)}")
            raise

    @staticmethod
    def parse_json(file_path: str) -> Any:
        """Parse JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise

    @staticmethod
    def parse_yaml(file_path: str) -> Any:
        """Parse YAML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"YAML parsing error: {str(e)}")
            raise

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"PDF parsing error: {str(e)}")
            raise

    @staticmethod
    def parse_file(file_path: str, file_type: str) -> Any:
        """Parse file based on type"""
        parsers = {
            'csv': FileParser.parse_csv,
            'xlsx': FileParser.parse_excel,
            'json': FileParser.parse_json,
            'yaml': FileParser.parse_yaml,
            'pdf': FileParser.parse_pdf,
        }

        parser = parsers.get(file_type)
        if not parser:
            raise ValueError(f"Unsupported file type: {file_type}")

        return parser(file_path)


class DataSummarizer:
    """Summarize data for LLM context"""

    @staticmethod
    def summarize_tabular_data(data: List[Dict[str, Any]], max_rows: int = 100) -> Dict[str, Any]:
        """Summarize tabular data"""
        if not data:
            return {}

        df = pd.DataFrame(data)
        
        summary = {
            "shape": {"rows": len(df), "columns": len(df.columns)},
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "sample_data": data[:min(max_rows, len(data))],
            "statistics": {}
        }

        # Add statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            summary["statistics"][col] = {
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()) if len(df) > 1 else 0
            }

        return summary

    @staticmethod
    def summarize_data(data: Any) -> Dict[str, Any]:
        """Summarize any data type"""
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return DataSummarizer.summarize_tabular_data(data)
        elif isinstance(data, dict):
            return {
                "type": "object",
                "keys": list(data.keys()),
                "sample": data
            }
        elif isinstance(data, str):
            return {
                "type": "text",
                "length": len(data),
                "preview": data[:500]
            }
        else:
            return {"type": "unknown", "data": str(data)[:500]}

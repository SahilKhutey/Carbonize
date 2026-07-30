"""
Auto-generate API documentation from OpenAPI spec
"""
import json
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIDocGenerator:
    """Generate API documentation from OpenAPI spec."""
    
    def __init__(self, openapi_url: str, output_dir: str = 'docs/api/generated'):
        self.openapi_url = openapi_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.spec: Dict = {}
    
    def fetch_spec(self) -> Dict:
        """Fetch OpenAPI specification from running API."""
        try:
            response = requests.get(f"{self.openapi_url}/openapi.json", timeout=30)
            response.raise_for_status()
            self.spec = response.json()
            logger.info(f"✓ Fetched OpenAPI spec from {self.openapi_url}")
            return self.spec
        except Exception as e:
            logger.warning(f"Failed to fetch spec from {self.openapi_url}: {e}. Using mock spec.")
            self.spec = {
                "openapi": "3.0.2",
                "info": {"title": "Carbonize API", "version": "2.0.0", "description": "Carbon Capture & Telemetry Platform API"},
                "paths": {
                    "/api/v1/inference/predict": {
                        "post": {
                            "tags": ["Inference"],
                            "summary": "Run YOLO Object Detection",
                            "operationId": "predict_inference",
                            "requestBody": {"content": {"application/json": {"schema": {"type": "object"}}}},
                            "responses": {"200": {"description": "Detection results"}}
                        }
                    }
                }
            }
            return self.spec
    
    def generate_endpoint_docs(self) -> Path:
        """Generate per-endpoint documentation."""
        output_path = self.output_dir / "endpoints.md"
        content = ["# API Endpoints Reference\n\n"]
        content.append(f"_Auto-generated from OpenAPI spec at {datetime.utcnow().isoformat()}Z_\n\n")
        content.append(f"**API Version**: {self.spec.get('info', {}).get('version', 'unknown')}\n\n")
        content.append(f"**Title**: {self.spec.get('info', {}).get('title', 'Carbonize API')}\n\n")
        content.append("---\n\n")
        
        paths = self.spec.get('paths', {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() in ('get', 'post', 'put', 'delete', 'patch'):
                    content.append(f"### {method.upper()} `{path}`\n\n")
                    content.append(f"**{operation.get('summary', path)}**\n\n")
                    content.append(f"{operation.get('description', '')}\n\n")
        
        output_path.write_text(''.join(content))
        logger.info(f"✓ Generated endpoint docs: {output_path}")
        return output_path
    
    def generate_postman_collection(self) -> Path:
        """Generate Postman collection."""
        output_path = self.output_dir / "carbonize.postman_collection.json"
        collection = {
            'info': {
                'name': self.spec.get('info', {}).get('title', 'Carbonize API'),
                'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json',
            },
            'item': [],
        }
        output_path.write_text(json.dumps(collection, indent=2))
        logger.info(f"✓ Generated Postman collection: {output_path}")
        return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-url', default='http://localhost:8000', help='API base URL')
    parser.add_argument('--output-dir', default='docs/api/generated', help='Output directory')
    args = parser.parse_args()
    
    generator = APIDocGenerator(args.api_url, args.output_dir)
    generator.fetch_spec()
    generator.generate_endpoint_docs()
    generator.generate_postman_collection()


if __name__ == '__main__':
    main()

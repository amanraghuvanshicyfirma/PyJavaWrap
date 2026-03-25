import requests
import json

class OpenAPIParser:
    def __init__(self, source):
        self.source = source
        self.spec = {}

    def load_spec(self):
        if self.source.startswith("http"):
            response = requests.get(self.source)
            self.spec = response.json()
        else:
            with open(self.source, 'r') as f:
                self.spec = json.load(f)

    def get_schemas(self):
        """Extracts components/schemas from the spec."""
        return self.spec.get("components", {}).get("schemas", {})

    def get_paths(self):
        """Extracts paths and their operations."""
        return self.spec.get("paths", {})

    def get_version(self):
        return self.spec.get("info", {}).get("version", "1.0.0")

    def get_title(self):
        return self.spec.get("info", {}).get("title", "FastAPIClient")

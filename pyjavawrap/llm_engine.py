import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class LLMEngine:
    def __init__(self, model_override: str = None):
        self.url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.model = model_override or os.getenv("OLLAMA_MODEL", "gpt-oss-cloud:120b")

    def generate_code(self, prompt: str):
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"

    def get_java_prompt(self, schema_json: str, type_name: str = "DTO"):
        if type_name == "DTO":
            return f"""
            You are an expert Java developer. 
            Generate a Java POJO class (with Jackson annotations and standard getters/setters) based on this JSON schema segment:
            {schema_json}
            
            Return ONLY the Java code. Do not include markdown code blocks.
            """
        else:
            return f"""
            You are an expert Java developer.
            Generate a Java Spring Boot RestClient or WebClient service based on these OpenAPI paths:
            {schema_json}
            
            Ensure the methods are type-safe and use the appropriate DTOs.
            Return ONLY the Java code. Do not include markdown code blocks.
            """

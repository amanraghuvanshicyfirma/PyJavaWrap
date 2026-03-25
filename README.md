# PyJavaWrap 🐍☕

Bridge the gap between Python (FastAPI) and Java with AI-powered code generation.

PyJavaWrap parses your FastAPI OpenAPI specification and uses **Ollama** (local LLM) to generate a type-safe Java client and DTOs.

## Features
- **Smart Mapping**: Maps complex Python types (Pydantic models) to Java POJOs.
- **AI-Powered**: Uses Ollama (GPT-OSS-Cloud / Qwen-Coder) for idiomatic Java generation.
- **Fast**: Generates a complete client structure in seconds.
- **Drop-in**: Seamlessly integrates into Spring Boot or standard Java projects.

## Installation
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Setup `.env`:
   ```bash
   OLLAMA_URL=http://localhost:11434/api/generate
   OLLAMA_MODEL=gpt-oss-cloud:120b
   ```

## Usage
1. Run your FastAPI application (or have an `openapi.json` ready):
   ```bash
   python examples/sample_api.py
   ```
2. Generate the Java client using the installed CLI:
   ```bash
   pyjavawrap http://localhost:8000/openapi.json -o generated_java -m qwen-coder-3-next
   ```

**CLI Options:**
- `source`: URL or path to the OpenAPI spec.
- `-o, --output`: Output directory (default: `generated_java`).
- `-p, --package`: Standard Java package name (default: `com.pyjavawrap.client`).
- `-m, --model`: Ollama model to use, overriding `.env`.

## Generated Structure
```text
generated_java/
├── SamplePythonAPIClient.java  <-- Main Client Service
└── model/
    ├── User.java               <-- Data Model (DTO)
    └── Item.java               <-- Data Model (DTO)
```

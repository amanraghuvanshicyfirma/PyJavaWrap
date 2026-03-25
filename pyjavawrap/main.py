import argparse
import os
import json
from pyjavawrap.parser import OpenAPIParser
from pyjavawrap.llm_engine import LLMEngine
from dotenv import load_dotenv

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="PyJavaWrap: Generate Java clients from FastAPI OpenAPI specs.")
    parser.add_argument("source", help="Path to openapi.json or URL to the running FastAPI app.")
    parser.add_argument("-o", "--output", default="generated_java", help="Output directory for Java files.")
    parser.add_argument("-p", "--package", default="com.pyjavawrap.client", help="Java package name.")
    parser.add_argument("-m", "--model", help="Ollama model to use (default: reads from .env or gpt-oss-cloud:120b).")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.output):
        os.makedirs(args.output)
        
    print(f"[*] Loading OpenAPI spec from {args.source}...")
    api_parser = OpenAPIParser(args.source)
    api_parser.load_spec()
    
    llm = LLMEngine(model_override=args.model)
    
    # 1. Generate Models (DTOs)
    schemas = api_parser.get_schemas()
    print(f"[*] Found {len(schemas)} schemas. Generating DTOs...")
    
    model_dir = os.path.join(args.output, "model")
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    for schema_name, schema_body in schemas.items():
        print(f"    - Generating {schema_name}.java...")
        prompt = llm.get_java_prompt(json.dumps(schema_body, indent=2), type_name="DTO")
        java_code = llm.generate_code(prompt)
        
        with open(os.path.join(model_dir, f"{schema_name}.java"), "w") as f:
            # Add package declaration if not present
            if "package" not in java_code:
                f.write(f"package {args.package}.model;\n\n")
            f.write(java_code)

    # 2. Generate Client
    print("[*] Generating Client Service...")
    paths = api_parser.get_paths()
    client_prompt = llm.get_java_prompt(json.dumps(paths, indent=2), type_name="Client")
    client_code = llm.generate_code(client_prompt)
    
    client_name = api_parser.get_title().replace(" ", "") + "Client"
    with open(os.path.join(args.output, f"{client_name}.java"), "w") as f:
        if "package" not in client_code:
            f.write(f"package {args.package};\n\n")
        f.write(client_code)

    print(f"[+] All files generated in {args.output}")

if __name__ == "__main__":
    main()

"""
Script to generate FastAPI application code from openapi.yaml.
This implements a spec-first approach where the OpenAPI spec is the source of truth.
"""
import subprocess
import sys
import os

def generate_code():
    """Generate FastAPI code from openapi.yaml"""
    if not os.path.exists("openapi.yaml"):
        print("❌ Error: openapi.yaml not found!")
        print("   Please create openapi.yaml first as the source of truth.")
        sys.exit(1)
    
    print("🔄 Generating FastAPI code from openapi.yaml...")
    
    try:
        # Generate code using fastapi-code-generator
        # The command name is 'fastapi-codegen' when installed via pip
        # -i: input file (OpenAPI spec)
        # -o: output directory
        # --model-file: where to put models (optional)
        # --router-file: where to put routers (optional)
        cmd = [
            "fastapi-codegen",
            "--input", "openapi.yaml",
            "--output", ".",
        ]
        
        # Add optional model and router file names if you want specific names
        # Otherwise, it will generate default names
        if os.path.exists("models.py") or os.path.exists("routers.py"):
            print("⚠️  Warning: models.py or routers.py already exists.")
            print("   They will be overwritten. Consider backing them up first.")
        
        subprocess.run(cmd, check=True)
        
        print("✅ Code generation completed!")
        print("📁 Generated files:")
        print("   - models.py (Pydantic models)")
        print("   - routers.py (FastAPI route handlers)")
        print("\n⚠️  Note: You'll need to manually integrate these into main.py")
        print("   or update your application structure to use the generated routers.")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during code generation: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: fastapi-codegen not found!")
        print("   Please install it: pip install fastapi-code-generator")
        sys.exit(1)

if __name__ == "__main__":
    generate_code()

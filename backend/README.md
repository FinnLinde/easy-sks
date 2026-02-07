# Easy SKS Backend

A minimal FastAPI application for the Easy SKS project using a **spec-first** development approach.

## Project Structure

```
backend/
├── openapi.yaml          # OpenAPI specification (source of truth)
├── main.py               # FastAPI app entry point
├── generate_from_spec.py # Script to generate code from openapi.yaml
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .gitignore           # Git ignore patterns
```

After running code generation, you'll also have:
- `models.py` - Generated Pydantic models
- `routers.py` - Generated route handlers

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative API docs (ReDoc): `http://localhost:8000/redoc`
- OpenAPI JSON schema: `http://localhost:8000/openapi.json`

## OpenAPI Support (Spec-First Approach)

This project uses a **spec-first** development approach, where the OpenAPI specification (`openapi.yaml`) is the source of truth. The FastAPI application code is generated from the OpenAPI spec, not the other way around.

### Workflow

1. **Define your API** in `openapi.yaml` (or `openapi.json`)
2. **Generate FastAPI code** from the spec using `fastapi-code-generator`
3. **Implement business logic** in the generated route handlers
4. **Regenerate code** whenever you update the OpenAPI spec

### Generating FastAPI Code from OpenAPI Spec

After defining or updating `openapi.yaml`, generate the FastAPI application code:

```bash
python generate_from_spec.py
```

Or directly using fastapi-code-generator:

```bash
fastapi-codegen --input openapi.yaml --output . --model-file models.py --router-file routers.py
```

This will generate:
- `models.py` - Pydantic models based on your schema definitions
- `routers.py` - FastAPI route handlers based on your path definitions

### Updating the OpenAPI Spec

Edit `openapi.yaml` to define:
- **Paths** - API endpoints and their operations
- **Schemas** - Request/response models
- **Parameters** - Query, path, and header parameters
- **Responses** - Response definitions and status codes

After updating the spec, regenerate the code and update your business logic implementations.

### Generating Client Code

You can use the OpenAPI Generator to create client code from the spec:

1. **Install OpenAPI Generator** (requires Java):
   ```bash
   # Using Homebrew (macOS):
   brew install openapi-generator
   
   # Or using npm:
   npm install -g @openapi-generator-plus/cli
   ```

2. **Generate TypeScript client** (for Next.js frontend):
   ```bash
   openapi-generator generate -i openapi.yaml -g typescript-axios -o ../frontend/src/api/generated
   ```

3. **Generate Python client**:
   ```bash
   openapi-generator generate -i openapi.yaml -g python -o ../clients/python
   ```

For more generators and options, visit: https://openapi-generator.tech/

## Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint
- `GET /openapi.json` - OpenAPI schema (JSON)

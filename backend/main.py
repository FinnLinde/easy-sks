"""
Main entry point for the FastAPI application.
This file should be kept minimal - most code is generated from openapi.yaml.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app instance
app = FastAPI(
    title="Easy SKS API",
    version="1.0.0",
    description="API for Easy SKS application",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include generated routers here after running generate_from_spec.py
# Example:
# from routers import router
# app.include_router(router)

# Temporary endpoints until code is generated from openapi.yaml
# These will be replaced by generated code
@app.get("/")
async def root():
    return {"message": "Welcome to Easy SKS API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

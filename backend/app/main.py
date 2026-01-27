from fastapi import FastAPI

from app.fsrs.api.routes import router as fsrs_router

app = FastAPI(
    title="easy-sks",
    description="Learning app for the SKS boating license.",
    version="0.1.0",
)

app.include_router(fsrs_router)


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {"message": "Welcome to the easy-sks API."}


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}

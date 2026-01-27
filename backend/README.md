# Backend (FastAPI)

This folder contains the initial FastAPI backend for easy-sks.

## Setup

From the `backend` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

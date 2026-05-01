# Easy SKS

Open-source study app for the German *Sportküstenschifferschein* (SKS) maritime
certificate. It bundles a flashcard system with FSRS spaced repetition,
full exam simulations, navigation-task practice, and optional AI-assisted
answer grading and audio transcription.

The app is designed to run **locally**: clone the repo, start a single
`docker compose` stack, and study in your browser.

## Quick start

Prerequisites: Docker and Docker Compose.

```bash
git clone https://github.com/<your-fork>/easy-sks.git
cd easy-sks
cp .env.example .env
docker compose up --build
```

Then open <http://localhost:3000>. The first run will:

- start a PostgreSQL container,
- run the database migrations,
- seed the bundled SKS card and navigation catalogues,
- start the FastAPI backend on `:8000` and the Next.js frontend on `:3000`.

The app works fully offline — no account, no login, no external services
required.

## Enabling AI features

By default Easy SKS evaluates answers with a built-in heuristic. If you supply
an OpenAI API key on the in-app **Settings** page, the following features are
upgraded to AI:

- **Answer grading** during study and exam sessions (uses an OpenAI chat
  model, default `gpt-4o-mini`).
- **Voice answers** — record an answer with your microphone and have it
  transcribed (default `gpt-4o-mini-transcribe`).

To enable:

1. Get an API key from <https://platform.openai.com>.
2. In the app, open **Settings** in the sidebar.
3. Toggle *KI-Funktionen aktivieren*, paste your key, hit **Speichern**.

The key is stored in your local Postgres `app_settings` table; changes take
effect immediately, no restart needed. To turn AI off again, untoggle the
switch or click *Key entfernen*.

## Local development (without Docker)

You'll need Python 3.12+, Node.js 20+, and a running Postgres reachable at
`postgresql://easy_sks:easy_sks@localhost:5432/easy_sks` (the easiest way is
`docker compose up db`).

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m scripts.seed --if-empty
uvicorn main:app --reload
```

API now on <http://localhost:8000>. Interactive docs at
<http://localhost:8000/docs>.

Run the test suite:

```bash
pytest
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>.

If you change the backend's OpenAPI surface, regenerate the typed client:

```bash
npm run generate-api
```

## Project layout

```
easy-sks/
├── backend/             FastAPI app (Python 3.12)
│   ├── card/            Card content
│   ├── study/           Spaced-repetition study sessions
│   ├── scheduling/      FSRS scheduling layer
│   ├── exam/            Full exam simulation
│   ├── navigation/      Navigation-task practice
│   ├── transcription/   OpenAI Whisper transcription
│   ├── settings/        DB-backed AI settings
│   ├── alembic/         Migrations
│   ├── scripts/seed.py  Seed script + bundled catalogues
│   └── tests/           Pytest suite
├── frontend/            Next.js 16 app (React 19, Tailwind CSS)
└── docker-compose.yml   Three-service stack: db + backend + frontend
```

## Tech stack

- **Backend**: FastAPI, SQLAlchemy 2 (async + asyncpg), Alembic, FSRS,
  OpenAI SDK, Pydantic v2.
- **Frontend**: Next.js 16 (App Router, standalone build), React 19,
  TailwindCSS 4, Radix UI, openapi-fetch (typed client generated from the
  backend's OpenAPI spec).
- **Database**: PostgreSQL 17.

## Contributing

Issues and pull requests welcome. The OpenAPI spec at `backend/openapi.yaml`
is the source of truth for the API contract — after backend changes,
regenerate it from the running app and run `npm run generate-api` in
`frontend/` to refresh the typed client.

## Disclaimer

Easy SKS is an unofficial study aid. The card catalogue is community-sourced
and the AI/heuristic grading may be wrong. Always verify against the
official SKS materials and your training instructor before relying on any
answer for the actual certification exam. The software is provided as-is
under the MIT License — no warranty, no liability.

## License

[MIT](LICENSE) © Finn Linde

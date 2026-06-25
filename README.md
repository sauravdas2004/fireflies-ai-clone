# Fireflies Clone

Compact clone of Fireflies.ai — meeting transcription, summaries, and action items.

## Project layout

- `backend/` — FastAPI application (SQLAlchemy + SQLite).
- `frontend/` — Next.js 14 (App Router), TypeScript, Tailwind CSS.

## Local setup

Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
# Initialize DB + seed
python -c "from app import seed; seed.seed_database()"
# Run dev server
uvicorn app.main:app --reload --port 8000
```

Frontend

```bash
cd frontend
npm install
npm run dev
# build
npm run build
```

## Environment

- `NEXT_PUBLIC_API_BASE_URL` defaults to `http://localhost:8000` (see `frontend/.env.example`).
- Backend CORS origins default to `http://localhost:3000`.

## Deployment notes

- Frontend can be deployed to Vercel; point the project root at the `frontend/` directory or use the included `frontend/vercel.json`.
- Backend can be containerized using `backend/Dockerfile` and deployed to any container host.

## Phase status

- Phase 1: DB models + seed — completed.
- Phase 2: FastAPI backend — completed.
- Phase 3: Next.js frontend — completed.
- Phase 4: polish — partially completed (tags, export, URL filters). Remaining: dark mode, global search UI, optional LLM QA.
- Phase 5: deployment & README — this README and basic deployment files were added.

## Helpful commands

- Run frontend build: `npm run build --prefix frontend`
- Run backend seed: `python -m backend.app.seed` (or see earlier seed command)

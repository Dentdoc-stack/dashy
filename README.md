# Dashy

This repo runs two servers:
- Backend API: FastAPI on http://localhost:8000
- Frontend UI: Next.js on http://localhost:3000

## Prerequisites
- Python 3.10+
- Node.js 18+

## Backend (FastAPI)

From the repo root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/health
```

## Frontend (Next.js)

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

The frontend reads the API base URL from `NEXT_PUBLIC_API_URL`. If you need a custom URL, create [frontend/.env.local](frontend/.env.local):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Run Both Servers

Open two terminals:
1. Start the backend with `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
2. Start the frontend with `npm run dev`

## Production (Optional)

Frontend:

```bash
cd frontend
npm run build
npm run start
```

Backend (no reload):

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```
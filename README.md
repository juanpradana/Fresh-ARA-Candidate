# Fresh ARA Candidate Screener

Web screener saham Indonesia untuk mendeteksi kandidat **Fresh ARA** berbasis pola H-1 (quiet accumulation) sesuai PRD `prd.md`.

## Scope v1

- Backend: FastAPI + SQLite + CLI pipeline skeleton
- Frontend: React + Vite + TypeScript + PWA scaffold
- API read-only (`/api/v1/*`)
- UI read-only (tanpa tombol refresh market data)

## Struktur Project

```text
app/
  backend/
    api/
    cli/
    core/
    repositories/
    scheduler/
    services/
  frontend/
docs/
tests/
prd.md
```

## Prasyarat

- Python 3.10+
- Node.js 18+
- npm

## Setup Cepat (Local)

### 1) Backend

Buat dan aktifkan virtual environment (Git Bash di Windows):

```bash
python -m venv .venv
source .venv/Scripts/activate
```

Install dependency backend dan inisialisasi DB:

```bash
pip install -r requirements.txt
python -c "from app.backend.core.db import init_db; init_db()"
```

Jalankan API:

```bash
uvicorn app.backend.api.app:app --reload
```

### 2) Frontend

```bash
npm --prefix app/frontend install
npm --prefix app/frontend run dev
```

### 3) Jalankan pipeline harian (skeleton)

```bash
python -m app.backend.cli.main run-daily --date YYYY-MM-DD
```

## Testing

Backend:

```bash
pytest tests/backend -v
```

Frontend:

```bash
npm --prefix app/frontend test
npm --prefix app/frontend run build
```

## Endpoint yang sudah tersedia (awal)

- `GET /api/v1/health`
- `GET /api/v1/screener`

## Dokumen

- PRD: `prd.md`
- Design spec: `docs/superpowers/specs/2026-05-06-fresh-ara-screener-design.md`
- Implementation plan: `docs/superpowers/plans/2026-05-06-fresh-ara-screener-implementation.md`
- Local runbook: `docs/local-runbook.md`

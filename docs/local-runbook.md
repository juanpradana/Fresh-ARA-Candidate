# Local Runbook

## A. Setup dasar

1. Install backend dependencies: `pip install -r requirements.txt`
2. Initialize database tables:
   - `python -c "from app.backend.core.db import init_db; init_db()"`
3. Start backend API:
   - `uvicorn app.backend.api.app:app --reload`
4. Install frontend dependencies:
   - `npm --prefix app/frontend install`
5. Start frontend dev server:
   - `npm --prefix app/frontend run dev`

## B. Skenario CLI operasional

### 1) First-time bootstrap data

```bash
python -m app.backend.cli.main backfill-market --start 2026-01-01 --end YYYY-MM-DD --qps 2 --batch-size 50
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 2 --batch-size 50
```

### 2) Rutinitas harian

```bash
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 2 --batch-size 50
```

### 3) Bandingkan preset

```bash
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset conservative
python -m app.backend.cli.main run-screening --date YYYY-MM-DD --preset aggressive
```

### 4) Recovery jika data kosong/tidak complete

```bash
python -m app.backend.cli.main update-market --date YYYY-MM-DD --qps 1 --batch-size 50
python -m app.backend.cli.main daily-smoke --date YYYY-MM-DD --qps 1 --batch-size 50
python -m app.backend.cli.main run-daily --date YYYY-MM-DD --preset balanced --qps 1 --batch-size 50
```

## C. Verifikasi cepat

- Backend tests: `pytest -q`
- Frontend tests: `npm --prefix app/frontend run test`
- Frontend build: `npm --prefix app/frontend run build`

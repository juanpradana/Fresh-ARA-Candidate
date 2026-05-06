# Local Runbook

1. Install backend dependencies: `pip install -r requirements.txt`
2. Initialize database tables:
   - `python -c "from app.backend.core.db import init_db; init_db()"`
3. Run daily pipeline skeleton:
   - `python -m app.backend.cli.main run-daily --date YYYY-MM-DD`
4. Start backend API:
   - `uvicorn app.backend.api.app:app --reload`
5. Install frontend dependencies:
   - `npm --prefix app/frontend install`
6. Start frontend dev server:
   - `npm --prefix app/frontend run dev`

# PRD — Web Screener “Fresh ARA Candidate”

**Versi:** 1.0  
**Tanggal:** 2026-05-06  
**Owner:** Farzani  
**Status:** Final (Approved)

## 1) Latar Belakang

Berdasarkan analisis 141 kasus **Fresh ARA** (ARA pertama, bukan chain), ditemukan pola dominan:

- H-1 cenderung **volume normal** (bukan spike): Vol_Ratio mean 1.03x, median 0.94x.
- H-1 sering **range sempit**: 47.4% pada Range_Pct 0.5–1.0.
- H-1 sering **price action tenang**: 55.6% kasus Price_Action < 0.7.
- Kombinasi ideal 3 indikator muncul di 21.5% kasus.

Insight inti: **“Quiet accumulation before explosive move.”**

---

## 2) Problem Statement

Trader kesulitan menyaring ratusan saham harian untuk menemukan kandidat yang **secara statistik** punya kemiripan pola H-1 sebelum fresh ARA. Proses manual lambat dan tidak konsisten.

---

## 3) Tujuan Produk

### 3.1 Business Goals
1. Menyediakan daftar kandidat fresh ARA besok secara otomatis setiap hari bursa.
2. Mempercepat proses screening dari manual menjadi < 3 menit.
3. Meningkatkan konsistensi keputusan berbasis rule statistik.

### 3.2 User Goals
1. User bisa melihat saham mana yang masuk “ideal setup”.
2. User bisa memfilter kriteria (agresif/konservatif).
3. User bisa menerima alert kandidat baru.

### 3.3 Non-Goals (v1)
- Bukan sistem auto-trading.
- Bukan prediksi pasti ARA.
- Tidak mencakup analisis fundamental mendalam real-time.

---

## 4) Scope Produk (Dikunci)

Aplikasi ini **read-only display**:
- Menampilkan hasil screening kandidat Fresh ARA.
- Menampilkan ranking, filter, detail indikator, histori sinyal.
- **Tidak** ada aksi trading / eksekusi order.
- **Tidak** ada tombol refresh data pasar di UI.

---

## 5) Jadwal Screening Harian

- Screening otomatis semua saham Indonesia setiap **18:00 WIB**.
- Job hanya jalan bila:
  1. Data EOD hari itu sudah tersedia.
  2. Job screening hari tersebut belum pernah sukses (idempotent guard).

---

## 6) Pengkondisian Anti-Limit (Rate Limit Safe)

1. **Request Throttler**: Batasi QPS (configurable).
2. **Batching**: Ambil data per batch ticker.
3. **Retry Policy**: Exponential backoff + jitter untuk 429/5xx.
4. **Circuit Breaker**: Pause sementara jika consecutive failure tinggi.
5. **Incremental Update**: Hanya fetch tanggal yang belum ada di DB.
6. **Caching & Dedupe**: Hindari request ganda ticker/tanggal sama.
7. **Job Lock**: Cegah dua job berjalan bersamaan.

---

## 7) Database Requirement

- Database utama: **SQLite**.
- Tabel minimum:
  - `tickers`
  - `prices_daily`
  - `features_daily`
  - `screening_results`
  - `screening_presets`
  - `job_runs`
  - `watchlists` (opsional)

### 7.1 Skema SQLite (Final)

```sql
CREATE TABLE IF NOT EXISTS tickers (
  ticker TEXT PRIMARY KEY,
  symbol TEXT NOT NULL,
  name TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  sector TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prices_daily (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trade_date TEXT NOT NULL,
  ticker TEXT NOT NULL,
  open REAL NOT NULL,
  high REAL NOT NULL,
  low REAL NOT NULL,
  close REAL NOT NULL,
  volume REAL NOT NULL,
  adj_close REAL,
  source TEXT NOT NULL DEFAULT 'yfinance',
  ingested_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (trade_date, ticker),
  FOREIGN KEY (ticker) REFERENCES tickers(ticker)
);

CREATE INDEX IF NOT EXISTS idx_prices_ticker_date ON prices_daily (ticker, trade_date);
CREATE INDEX IF NOT EXISTS idx_prices_date ON prices_daily (trade_date);

CREATE TABLE IF NOT EXISTS features_daily (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trade_date TEXT NOT NULL,
  ticker TEXT NOT NULL,
  vol_ratio REAL,
  range_pct REAL,
  price_action REAL,
  is_ara_t0 INTEGER NOT NULL DEFAULT 0,
  range_narrowing INTEGER,
  liquidity_score REAL,
  feature_version TEXT NOT NULL DEFAULT 'v1',
  computed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (trade_date, ticker, feature_version),
  FOREIGN KEY (ticker) REFERENCES tickers(ticker)
);

CREATE INDEX IF NOT EXISTS idx_features_date ON features_daily (trade_date);
CREATE INDEX IF NOT EXISTS idx_features_ticker_date ON features_daily (ticker, trade_date);

CREATE TABLE IF NOT EXISTS screening_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  screen_date TEXT NOT NULL,
  feature_date TEXT NOT NULL,
  ticker TEXT NOT NULL,
  preset_name TEXT NOT NULL,
  score REAL NOT NULL,
  rank_num INTEGER NOT NULL,
  pass_vol_ratio INTEGER NOT NULL,
  pass_range_pct INTEGER NOT NULL,
  pass_price_action INTEGER NOT NULL,
  pass_is_ara_t0 INTEGER NOT NULL,
  pass_count INTEGER NOT NULL,
  category TEXT NOT NULL,
  reason_json TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (screen_date, ticker, preset_name)
);

CREATE INDEX IF NOT EXISTS idx_screen_date_rank ON screening_results (screen_date, rank_num);
CREATE INDEX IF NOT EXISTS idx_screen_ticker ON screening_results (ticker, screen_date);

CREATE TABLE IF NOT EXISTS screening_presets (
  preset_name TEXT PRIMARY KEY,
  min_vol_ratio REAL NOT NULL,
  max_vol_ratio REAL NOT NULL,
  min_range_pct REAL NOT NULL,
  max_range_pct REAL NOT NULL,
  max_price_action REAL NOT NULL,
  require_not_ara INTEGER NOT NULL DEFAULT 1,
  score_weights_json TEXT NOT NULL,
  is_default INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_name TEXT NOT NULL,
  run_date TEXT NOT NULL,
  started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  status TEXT NOT NULL,
  rows_affected INTEGER DEFAULT 0,
  error_message TEXT,
  meta_json TEXT,
  UNIQUE (job_name, run_date, status)
);

CREATE INDEX IF NOT EXISTS idx_job_runs_name_date ON job_runs (job_name, run_date);

CREATE TABLE IF NOT EXISTS watchlists (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  watchlist_name TEXT NOT NULL,
  ticker TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (watchlist_name, ticker)
);
```

---

## 8) Definisi Rule Screening Default

```python
def is_fresh_ara_candidate(row):
    return (
        0.75 <= row["Vol_Ratio"] <= 1.25 and
        0.50 <= row["Range_Pct"] <= 1.00 and
        row["Price_Action"] < 0.70 and
        row["Is_ARA_T0"] == 0
    )
```

Preset:
- **Conservative:** Price_Action < 0.5, Range 0.5–0.9
- **Balanced (default):** rule default
- **Aggressive:** Vol 0.7–1.3, Range 0.5–1.2, Price_Action < 0.8

---

## 9) API Requirement (Read-Only)

Base: `/api/v1`

- `GET /health`
- `GET /meta/latest-screen-date`
- `GET /meta/presets`
- `GET /screener?screen_date=YYYY-MM-DD&preset=balanced&limit=100&offset=0`
- `GET /screener/{ticker}?screen_date=YYYY-MM-DD&preset=balanced`
- `GET /screener/{ticker}/history?start=YYYY-MM-DD&end=YYYY-MM-DD&preset=balanced`
- `GET /analytics/distribution?screen_date=YYYY-MM-DD&preset=balanced`
- `GET /analytics/backtest?start=YYYY-MM-DD&end=YYYY-MM-DD&preset=balanced&top_n=20`
- `GET /export/screener.csv?screen_date=YYYY-MM-DD&preset=balanced`
- `GET /export/screener.xlsx?screen_date=YYYY-MM-DD&preset=balanced`

**Catatan:** Tidak ada endpoint refresh market data.

---

## 10) CLI Requirement (Manual via Terminal)

Entry-point:

```bash
python -m app.backend.cli.main <command> [options]
```

Command:
- `update-market --date YYYY-MM-DD [--batch-size N] [--qps N]`
- `backfill-market --start YYYY-MM-DD --end YYYY-MM-DD [--qps N]`
- `compute-features --date YYYY-MM-DD [--feature-version v1]`
- `run-screening --date YYYY-MM-DD [--preset balanced]`
- `run-daily --date YYYY-MM-DD [--preset balanced]`
- `schedule-screening --timezone Asia/Jakarta`

Contoh:

```bash
python -m app.backend.cli.main update-market --date 2026-05-06
python -m app.backend.cli.main compute-features --date 2026-05-06
python -m app.backend.cli.main run-screening --date 2026-05-06 --preset balanced
```

---

## 11) UI/UX Requirement

- Format aplikasi: **Web**.
- **Mobile-friendly** (responsive).
- **Installable multiplatform** melalui **PWA**.
- Aplikasi hanya menampilkan data/sinyal (read-only).
- Tidak ada tombol refresh data pasar di UI.

---

## 12) Project Structure (Development Friendly)

```text
app/
  backend/
    api/
      routers/
      schemas/
      deps/
    services/
      market_data/
      feature_engineering/
      screening/
      scoring/
    repositories/
      sqlite/
    scheduler/
    cli/
      main.py
      commands/
    core/
      config.py
      logging.py
      db.py
  frontend/
    src/
      app/
      pages/
      widgets/
      features/
        screener/
        ticker-detail/
        analytics/
      shared/
        api/
        ui/
        hooks/
  tests/
    backend/
    frontend/
  scripts/
  docs/
```

Prinsip:
- Algoritma screening dipisah dari endpoint.
- Komponen UI modular per fitur.
- Config preset/rule externalized.

---

## 13) NFR (Non-Functional Requirements)

1. Load screener < 2 detik untuk ~1.000 ticker.
2. Job 18:00 WIB retry-safe dan idempotent.
3. Logging terstruktur untuk audit pipeline.
4. Data freshness indicator wajib tampil.
5. Uptime aplikasi minimal 99.5% (jam trading).

---

## 14) KPI

### KPI Model/Sinyal
- Precision fresh ARA next day
- Recall terhadap seluruh fresh ARA
- Precision@Top10 / Top20
- Stabilitas performa rolling 3 bulan

### KPI Produk
- Daily active users screener
- Waktu rata-rata screening session
- Watchlist conversion rate
- Alert open rate

---

## 15) Risiko & Mitigasi

1. False positive tinggi → preset konservatif + transparansi score.
2. Data lag/invalid → freshness warning + block jika data belum complete.
3. Regime market berubah → recalibration threshold berkala.
4. Overfitting dataset historis → walk-forward & out-of-sample test.

---

## 16) Compliance & Disclaimer

- Sinyal bersifat probabilistik, bukan jaminan hasil.
- Tampilkan disclaimer jelas di aplikasi.
- Simpan audit trail perubahan rule/preset.

---

## 17) Acceptance Criteria (UAT)

1. Preset Balanced menghasilkan kandidat harian tanpa error.
2. Filter custom mengubah hasil query dengan cepat.
3. Detail ticker menampilkan indikator + pass/fail rule.
4. Backtest menampilkan metrik valid sesuai periode.
5. Alert (jika diaktifkan) terkirim sesuai trigger.
6. Data freshness warning muncul saat data belum final.

---

## 18) Keputusan Produk Terkunci

- Owner = **Farzani**
- DB = **SQLite**
- Screening otomatis = **18:00 WIB**
- Proteksi limit = **Wajib**
- Refresh data pasar = **CLI manual di terminal**
- UI = **Read-only, tanpa tombol refresh data**
- Aplikasi = **Web mobile-friendly + installable PWA multiplatform**

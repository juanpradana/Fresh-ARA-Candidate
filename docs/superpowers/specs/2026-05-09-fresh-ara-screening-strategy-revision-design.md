# Design Spec — Fresh ARA Screening Strategy Revision (v1.1)

Tanggal: 2026-05-09  
Status: Approved for implementation planning

## 1) Tujuan Revisi

Meningkatkan kualitas sinyal Fresh ARA dengan tetap mempertahankan fondasi yang sudah kuat (rule explainable + ranking score), melalui:

1. Penyelarasan definisi volume ratio dengan basis statistik dataset.
2. Pengetatan definisi “fresh” agar tidak tercampur chain ARA.
3. Preset threshold yang benar-benar dinamis di core logic.
4. Scoring granular (tiered), bukan dominan binary.
5. Penambahan sinyal squeeze sebagai bonus (opsional), bukan hard filter.

## 2) In-Scope dan Out-of-Scope

### In-Scope
- Perubahan logika feature engineering, screening, scoring, dan evaluasi backtest.
- Penyesuaian struktur data output screening agar lebih kaya explainability.
- Penambahan metrik evaluasi untuk validasi kualitas sinyal.

### Out-of-Scope
- Integrasi broker / auto-trading.
- Perubahan arsitektur besar di luar domain screening.
- Perubahan UI besar selain penyesuaian field baru jika diperlukan.

## 3) Keputusan Desain

## 3.1 Komponen yang Dipertahankan
- Threshold baseline balanced (`vol_ratio`, `range_pct`, `price_action`) tetap menjadi acuan.
- Pass-count sebagai explainability utama tetap dipertahankan.
- Continuous score untuk ranking tetap dipertahankan.
- Preset conservative/balanced/aggressive tetap dipakai sebagai antarmuka strategi.

## 3.2 Perubahan Wajib

### A. Definisi Volume Ratio
- Default strategis: gunakan `vol_ratio_5d` sebagai metrik utama.
- Opsi lanjutan: hybrid ratio (3d/5d/20d) diperbolehkan jika dibutuhkan, tetapi harus eksplisit dan konsisten.
- Semua threshold vol ratio diterapkan ke metrik volume yang sama dengan evaluasi statistik.

### B. Freshness Hard Filter
- Tambahkan `days_since_last_ara`.
- Hard rule freshness: `days_since_last_ara >= 5`.
- Nilai sentinel “tidak ada riwayat ARA” (mis. 999) diperlakukan sebagai sangat fresh.

### C. Dynamic Preset di Core Screening
- Core screening harus menerima threshold dari preset aktif.
- Tidak boleh ada threshold hardcoded balanced di evaluasi pass/fail utama.

### D. Tiered Scoring
- `price_action` wajib tiered:
  - `< 0.30 => 1.0`
  - `0.30–0.50 => 0.8`
  - `0.50–0.70 => 0.6`
  - `>= 0.70 => 0.0`
- `vol_ratio` dan `range_pct` disarankan mengikuti pola tiered untuk granularitas setara.

### E. Bonus BB Squeeze
- Tambah `is_bb_squeeze_20` sebagai bonus score (opsional).
- Bonus direkomendasikan dalam rentang `+0.1` sampai `+0.2`.
- `is_bb_squeeze_20` tidak menjadi hard filter default.

## 4) Konfigurasi Preset Target

### Conservative
- `vol_ratio`: `0.85–1.15`
- `range_pct`: `0.50–0.85`
- `price_action`: `< 0.50`

### Balanced (default)
- `vol_ratio`: `0.75–1.25`
- `range_pct`: `0.50–1.00`
- `price_action`: `< 0.70`

### Aggressive
- `vol_ratio`: `0.60–1.40`
- `range_pct`: `0.40–1.20`
- `price_action`: `< 0.90`

## 5) Data Contract Target (Logical)

Output screening direkomendasikan memuat blok berikut:

- `candidate`: identitas kandidat + harga + ground truth backtest.
- `indicators`: nilai indikator mentah (`vol_ratio_5d`, `range_pct`, `price_action`, `days_since_last_ara`, `is_bb_squeeze_20`).
- `screening_result`: hasil pass/fail per rule + `pass_count`.
- `scoring`: subscore per indikator + bonus + `final_score`.
- `metadata`: preset aktif + timestamp screening.

Kontrak API tetap memakai envelope konsisten:
- `data`
- `meta`
- `error`

## 6) Metrik Evaluasi Wajib (Backtesting)

1. **Hit Rate (1-day)**
2. **Hit Rate (3-day)**
3. **Precision@TopN**
4. **Average score on hit vs miss**
5. **Distribution by pass_count**

Metrik ini harus dapat dibandingkan antar preset untuk tuning threshold.

## 7) Dampak Domain Model

Perluasan field domain yang dipertimbangkan:
- `vol_ratio_5d` (atau canonical volume ratio baru)
- `days_since_last_ara`
- `is_bb_squeeze_20`
- `pass_fresh_check`
- Subscore granular (`score_vol_ratio`, `score_range_pct`, `score_price_action`, `score_bonus_bb_squeeze`)

Prinsip kompatibilitas:
- Endpoint lama tetap hidup.
- Field baru bersifat additive agar tidak memutus consumer lama.

## 8) Risiko dan Mitigasi

1. **Distribusi kandidat turun drastis** setelah fresh filter.
   - Mitigasi: monitor perubahan jumlah kandidat per preset.
2. **Overfitting scoring tiered**.
   - Mitigasi: validasi lintas rentang tanggal + bandingkan hit/miss score separation.
3. **Kontrak frontend pecah karena field tambahan**.
   - Mitigasi: additive contract + update tipe client bertahap.

## 9) Acceptance Criteria Revisi

1. Preset memengaruhi hasil screening di core (bukan sekadar metadata).
2. `days_since_last_ara >= 5` aktif sebagai hard freshness filter.
3. Scoring tiered berjalan untuk `price_action` dan tervalidasi boundary.
4. `vol_ratio` konsisten definisi dengan dataset statistik yang dipakai evaluasi.
5. Backtest menyediakan metrik evaluasi tambahan yang disepakati.
6. API/UI tetap kompatibel dan test suite tetap hijau.

## 10) Exit Criteria

Revisi dianggap selesai ketika:
- Perubahan logika aktif end-to-end di pipeline harian.
- Metrik evaluasi baru tersedia dari API analytics.
- Dokumentasi threshold/preset diperbarui.
- Tidak ada regresi pada test existing kritikal.
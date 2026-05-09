# Baseline Backtest Metrics (Balanced)

Tanggal freeze: 2026-05-09  
Window: `2026-05-01` s/d `2026-05-31`  
Preset: `balanced`  
Top N: `20`

```json
{
  "avg_score": 0.7623277777777778,
  "avg_score_hit": 0.904,
  "avg_score_miss": 0.7078384615384615,
  "distribution_by_pass_count": {
    "2": 2,
    "3": 11,
    "4": 5
  },
  "hit_rate_1d": 0.2777777777777778,
  "hit_rate_3d": 0.2777777777777778,
  "precision_at_top_n": 0.2777777777777778,
  "total": 18,
  "win_rate": 0.2777777777777778
}
```

## Notes

- Snapshot ini dipakai sebagai baseline sebelum eksperimen lanjutan (mis. BB squeeze bonus).
- Command sumber metrik:
  - `get_backtest_summary(start='2026-05-01', end='2026-05-31', preset='balanced', top_n=20)`

import argparse
import json
import sys
from datetime import datetime

from app.backend.cli.commands.backfill_market import handle_backfill_market
from app.backend.cli.commands.compute_features import handle_compute_features
from app.backend.cli.commands.run_screening import handle_run_screening
from app.backend.cli.commands.schedule_screening import handle_schedule_screening
from app.backend.cli.commands.update_market import handle_update_market
from app.backend.core.db import init_db
from app.backend.services.alerts.service import capture_system_alarm, capture_watchlist_alerts
from app.backend.services.feature_engineering.service import compute_features
from app.backend.services.market_data.service import fetch_daily_market_data
from app.backend.services.scoring.service import score_candidate
from app.backend.services.screening.service import is_fresh_ara_candidate
from app.backend.services.universe.service import get_default_idx_universe
from app.backend.repositories.sqlite.repo import (
    finish_job_run_failed,
    finish_job_run_skipped,
    finish_job_run_success,
    try_start_job_run,
    upsert_screening_result,
)


def _run_daily(date: str, batch_size: int = 50) -> None:
    tickers = get_default_idx_universe()

    for index in range(0, len(tickers), batch_size):
        batch = tickers[index:index + batch_size]
        for ticker in batch:
            data_rows = fetch_daily_market_data(ticker, date)
            for row in data_rows:
                features = compute_features(row)
                passed = is_fresh_ara_candidate(features)
                score = score_candidate(features)
                pass_count = sum(
                    [
                        1 if 0.75 <= features["vol_ratio"] <= 1.25 else 0,
                        1 if 0.50 <= features["range_pct"] <= 1.00 else 0,
                        1 if features["price_action"] < 0.70 else 0,
                        1 if int(features["is_ara_t0"]) == 0 else 0,
                    ]
                )
                upsert_screening_result(
                    screen_date=date,
                    ticker=row["ticker"],
                    preset_name="balanced",
                    score=score,
                    pass_count=pass_count,
                    category="ideal" if passed else "candidate",
                )


def _now_iso() -> str:
    return datetime.utcnow().isoformat()


def _emit_system_alarm(run_date: str, code: str) -> bool:
    try:
        return capture_system_alarm(run_date=run_date, code=code)
    except Exception:
        return False


def handle_run_daily(
    date: str,
    preset: str,
    batch_size: int,
    qps: float,
    universe_mode: str = "external_live",
    raise_on_error: bool = True,
) -> dict:
    init_db()
    started = try_start_job_run(run_date=date, started_at=_now_iso())
    if not started:
        return {"status": "skipped", "error": "already running or already executed"}

    fetched = 0
    meta_json_obj: dict[str, object] = {
        "expected": 0,
        "fetched": 0,
        "preset": preset,
        "market_status": "empty",
        "tickers_ok": 0,
        "tickers_empty": 0,
        "tickers_error": 0,
        "rows_upserted": 0,
        "batch_count": 0,
        "universe_mode": universe_mode,
        "universe_source": "unknown",
        "universe_count": 0,
        "universe_fallback": False,
    }
    meta_json = json.dumps(meta_json_obj, separators=(",", ":"))
    try:
        update_result = handle_update_market(date, batch_size, qps, universe_mode=universe_mode)
        expected = int(update_result.get("expected", 0))
        fetched = int(update_result.get("fetched", 0))
        tickers_ok = int(update_result.get("tickers_ok", 0))
        tickers_empty = int(update_result.get("tickers_empty", 0))
        tickers_error = int(update_result.get("tickers_error", 0))
        rows_upserted = int(update_result.get("rows_upserted", 0))
        batch_count = int(update_result.get("batch_count", 0))
        market_status = "complete" if update_result.get("is_complete", False) else ("empty" if fetched == 0 else "partial")
        universe_source = str(update_result.get("universe_source", "unknown"))
        universe_count = int(update_result.get("universe_count", 0))
        universe_fallback = bool(update_result.get("universe_fallback", False))
        meta_json_obj = {
            "expected": expected,
            "fetched": fetched,
            "preset": preset,
            "market_status": market_status,
            "tickers_ok": tickers_ok,
            "tickers_empty": tickers_empty,
            "tickers_error": tickers_error,
            "rows_upserted": rows_upserted,
            "batch_count": batch_count,
            "universe_mode": universe_mode,
            "universe_source": universe_source,
            "universe_count": universe_count,
            "universe_fallback": universe_fallback,
        }
        meta_json = json.dumps(meta_json_obj, separators=(",", ":"))

        if not update_result.get("is_complete", False):
            if expected > 0 and fetched == 0:
                _emit_system_alarm(run_date=date, code="system.no_market_data")
                finish_job_run_skipped(
                    run_date=date,
                    finished_at=_now_iso(),
                    message="no market data",
                    rows_affected=0,
                    meta_json=meta_json,
                )
                return {"status": "skipped", "error": "no market data"}

            _emit_system_alarm(run_date=date, code="system.market_data_incomplete")
            finish_job_run_failed(
                run_date=date,
                finished_at=_now_iso(),
                error_message="market data incomplete",
                rows_affected=fetched,
                meta_json=meta_json,
            )
            return {"status": "failed", "error": "market data incomplete"}

        handle_compute_features(date, "v1")
        handle_run_screening(date, preset)
        capture_watchlist_alerts(run_date=date, preset=preset)
        finish_job_run_success(
            run_date=date,
            finished_at=_now_iso(),
            rows_affected=fetched,
            meta_json=meta_json,
        )
        return {"status": "success", "error": None}
    except Exception as exc:
        _emit_system_alarm(run_date=date, code=f"system.exception.{type(exc).__name__}")
        finish_job_run_failed(
            run_date=date,
            finished_at=_now_iso(),
            error_message=str(exc),
            rows_affected=fetched,
            meta_json=meta_json,
        )
        if raise_on_error:
            raise
        return {"status": "failed", "error": str(exc)}


def handle_daily_smoke(date: str, batch_size: int, qps: float, universe_mode: str = "external_live") -> dict:
    return handle_run_daily(
        date=date,
        preset="balanced",
        batch_size=batch_size,
        qps=qps,
        universe_mode=universe_mode,
        raise_on_error=False,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    update_market_parser = subparsers.add_parser("update-market")
    update_market_parser.add_argument("--date", required=True)
    update_market_parser.add_argument("--batch-size", type=int, default=50)
    update_market_parser.add_argument("--qps", type=float, default=2.0)
    update_market_parser.add_argument("--universe-mode", default="external_live")

    backfill_market_parser = subparsers.add_parser("backfill-market")
    backfill_market_parser.add_argument("--start", required=True)
    backfill_market_parser.add_argument("--end", required=True)
    backfill_market_parser.add_argument("--qps", type=float, default=2.0)
    backfill_market_parser.add_argument("--batch-size", type=int, default=50)

    compute_features_parser = subparsers.add_parser("compute-features")
    compute_features_parser.add_argument("--date", required=True)
    compute_features_parser.add_argument("--feature-version", default="v1")

    run_screening_parser = subparsers.add_parser("run-screening")
    run_screening_parser.add_argument("--date", required=True)
    run_screening_parser.add_argument("--preset", default="balanced")

    run_daily_parser = subparsers.add_parser("run-daily")
    run_daily_parser.add_argument("--date", required=True)
    run_daily_parser.add_argument("--preset", default="balanced")
    run_daily_parser.add_argument("--batch-size", type=int, default=50)
    run_daily_parser.add_argument("--qps", type=float, default=2.0)
    run_daily_parser.add_argument("--universe-mode", default="external_live")

    schedule_screening_parser = subparsers.add_parser("schedule-screening")
    schedule_screening_parser.add_argument("--timezone", default="Asia/Jakarta")

    daily_smoke_parser = subparsers.add_parser("daily-smoke")
    daily_smoke_parser.add_argument("--date", required=True)
    daily_smoke_parser.add_argument("--batch-size", type=int, default=50)
    daily_smoke_parser.add_argument("--qps", type=float, default=2.0)
    daily_smoke_parser.add_argument("--universe-mode", default="external_live")

    args = parser.parse_args()

    if args.command == "update-market":
        result = handle_update_market(args.date, args.batch_size, args.qps, universe_mode=args.universe_mode)
        if not result.get("is_complete", False):
            print(
                f"[ALERT][MARKET] date={args.date} fetched={result.get('fetched', 0)} expected={result.get('expected', 0)} source={result.get('universe_source', 'unknown')}"
            )
        return

    if args.command == "backfill-market":
        handle_backfill_market(args.start, args.end, args.qps, args.batch_size)
        return

    if args.command == "compute-features":
        handle_compute_features(args.date, args.feature_version)
        return

    if args.command == "run-screening":
        handle_run_screening(args.date, args.preset)
        return

    if args.command == "run-daily":
        handle_run_daily(args.date, args.preset, args.batch_size, args.qps, universe_mode=args.universe_mode)
        return

    if args.command == "schedule-screening":
        handle_schedule_screening(args.timezone)
        return

    if args.command == "daily-smoke":
        result = handle_daily_smoke(args.date, args.batch_size, args.qps, universe_mode=args.universe_mode)
        status = str(result.get("status", "failed"))
        error = result.get("error")
        if status == "success":
            print(f"[SMOKE][OK] run_date={args.date}")
            return
        if status == "skipped":
            reason = "none" if error is None else str(error)
            print(f"[SMOKE][SKIPPED] run_date={args.date} reason={reason}")
            return
        message = "unknown" if error is None else str(error)
        print(f"[SMOKE][ALERT] run_date={args.date} error={message}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()

import argparse

from app.backend.cli.commands.backfill_market import handle_backfill_market
from app.backend.cli.commands.compute_features import handle_compute_features
from app.backend.cli.commands.run_screening import handle_run_screening
from app.backend.cli.commands.schedule_screening import handle_schedule_screening
from app.backend.cli.commands.update_market import handle_update_market
from app.backend.services.daily_job.service import run_daily_job
from app.backend.services.feature_engineering.service import compute_features
from app.backend.services.market_data.service import fetch_daily_market_data
from app.backend.services.scoring.service import score_candidate
from app.backend.services.screening.service import is_fresh_ara_candidate
from app.backend.services.universe.service import get_default_idx_universe
from app.backend.repositories.sqlite.repo import upsert_screening_result


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


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    update_market_parser = subparsers.add_parser("update-market")
    update_market_parser.add_argument("--date", required=True)
    update_market_parser.add_argument("--batch-size", type=int, default=50)
    update_market_parser.add_argument("--qps", type=float, default=2.0)

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

    schedule_screening_parser = subparsers.add_parser("schedule-screening")
    schedule_screening_parser.add_argument("--timezone", default="Asia/Jakarta")

    args = parser.parse_args()

    if args.command == "update-market":
        handle_update_market(args.date, args.batch_size, args.qps)
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
        update_result = handle_update_market(args.date, args.batch_size, args.qps)
        if not update_result.get("is_complete", False):
            return
        handle_compute_features(args.date, "v1")
        handle_run_screening(args.date, args.preset)
        return

    if args.command == "schedule-screening":
        handle_schedule_screening(args.timezone)
        return


if __name__ == "__main__":
    main()

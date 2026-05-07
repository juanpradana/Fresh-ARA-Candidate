import argparse

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import upsert_screening_result
from app.backend.services.daily_job.service import run_daily_job
from app.backend.services.feature_engineering.service import compute_features
from app.backend.services.market_data.service import fetch_daily_market_data
from app.backend.services.scoring.service import score_candidate
from app.backend.services.screening.service import is_fresh_ara_candidate
from app.backend.services.universe.service import get_default_idx_universe


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
    parser.add_argument("command")
    parser.add_argument("--date")
    args = parser.parse_args()

    if args.command == "run-daily" and args.date:
        run_daily_job(args.date)
        return

    print(args.command, args.date)


if __name__ == "__main__":
    main()

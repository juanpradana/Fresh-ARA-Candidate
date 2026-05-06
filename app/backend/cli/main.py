import argparse

from app.backend.core.db import init_db
from app.backend.repositories.sqlite.repo import seed_daily_result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("--date")
    args = parser.parse_args()

    if args.command == "run-daily" and args.date:
        init_db()
        seed_daily_result(args.date)
        return

    print(args.command, args.date)


if __name__ == "__main__":
    main()

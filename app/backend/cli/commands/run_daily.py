def should_skip_run(run_date: str, successful_dates: list[str]) -> bool:
    return run_date in successful_dates

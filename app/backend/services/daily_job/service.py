def run_daily_job(run_date: str, batch_size: int = 50) -> dict:
    from app.backend.cli.main import handle_run_daily

    result = handle_run_daily(
        date=run_date,
        preset="balanced",
        batch_size=batch_size,
        qps=2.0,
        raise_on_error=False,
    )
    status = str(result.get("status", "failed"))
    error = result.get("error")
    return {
        "status": status,
        "skipped": status == "skipped",
        "error": error,
    }

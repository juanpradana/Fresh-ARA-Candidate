from app.backend.cli.commands.run_daily import should_skip_run


def test_should_skip_when_job_already_successful():
    assert should_skip_run("2026-05-06", ["2026-05-06"]) is True

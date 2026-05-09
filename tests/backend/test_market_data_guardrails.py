from app.backend.services.market_data.guardrails import (
    CircuitBreaker,
    RequestCache,
    RateLimiter,
    retry_with_backoff,
)


def test_rate_limiter_waits_for_qps(monkeypatch):
    sleeps: list[float] = []
    now = {"value": 100.0}

    def fake_monotonic() -> float:
        return now["value"]

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)
        now["value"] += seconds

    limiter = RateLimiter(qps=2.0, monotonic=fake_monotonic, sleeper=fake_sleep)

    limiter.wait()
    limiter.wait()

    assert sleeps and sleeps[0] > 0


def test_retry_with_backoff_retries_then_succeeds_for_transient_error(monkeypatch):
    attempts = {"count": 0}
    sleeps: list[float] = []

    def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("temporary 429")
        return "ok"

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    result = retry_with_backoff(
        operation=flaky,
        max_attempts=3,
        base_delay=0.1,
        max_delay=1.0,
        jitter_ratio=0.0,
        sleeper=fake_sleep,
        should_retry=lambda exc: "429" in str(exc),
    )

    assert result == "ok"
    assert attempts["count"] == 3
    assert sleeps == [0.1, 0.2]


def test_retry_with_backoff_does_not_retry_for_non_transient_error(monkeypatch):
    attempts = {"count": 0}
    sleeps: list[float] = []

    def non_transient() -> str:
        attempts["count"] += 1
        raise ValueError("invalid ticker symbol")

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    try:
        retry_with_backoff(
            operation=non_transient,
            max_attempts=3,
            base_delay=0.1,
            max_delay=1.0,
            jitter_ratio=0.0,
            sleeper=fake_sleep,
            should_retry=lambda exc: "429" in str(exc),
        )
    except ValueError as exc:
        assert "invalid ticker symbol" in str(exc)
    else:
        raise AssertionError("expected ValueError")

    assert attempts["count"] == 1
    assert sleeps == []


def test_circuit_breaker_opens_after_failures(monkeypatch):
    now = {"value": 10.0}

    def fake_monotonic() -> float:
        return now["value"]

    breaker = CircuitBreaker(failure_threshold=2, reset_timeout=5.0, monotonic=fake_monotonic)

    assert breaker.allow() is True
    breaker.record_failure()
    assert breaker.allow() is True
    breaker.record_failure()

    assert breaker.allow() is False

    now["value"] += 5.1
    assert breaker.allow() is True


def test_request_cache_dedupes_key():
    cache = RequestCache()

    assert cache.has(("BBCA.JK", "2026-05-07")) is False
    cache.set(("BBCA.JK", "2026-05-07"), [{"ticker": "BBCA.JK"}])
    assert cache.has(("BBCA.JK", "2026-05-07")) is True
    assert cache.get(("BBCA.JK", "2026-05-07")) == [{"ticker": "BBCA.JK"}]


def test_rate_limiter_emits_wait_event():
    events: list[dict[str, object]] = []
    now = {"value": 100.0}

    def fake_monotonic() -> float:
        return now["value"]

    def fake_sleep(seconds: float) -> None:
        now["value"] += seconds

    limiter = RateLimiter(
        qps=2.0,
        monotonic=fake_monotonic,
        sleeper=fake_sleep,
        on_event=events.append,
    )

    limiter.wait()
    limiter.wait()

    assert events and events[0]["event"] == "guardrail.rate_limit_wait"
    assert events[0]["qps"] == 2.0
    assert float(events[0]["sleep_sec"]) > 0


def test_retry_with_backoff_emits_retry_events():
    attempts = {"count": 0}
    events: list[dict[str, object]] = []

    def flaky() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("temporary 429")
        return "ok"

    result = retry_with_backoff(
        operation=flaky,
        max_attempts=3,
        base_delay=0.1,
        max_delay=1.0,
        jitter_ratio=0.0,
        sleeper=lambda _: None,
        should_retry=lambda exc: "429" in str(exc),
        on_event=events.append,
    )

    assert result == "ok"
    assert len(events) == 2
    assert [event["event"] for event in events] == [
        "guardrail.retry_scheduled",
        "guardrail.retry_scheduled",
    ]
    assert events[0]["attempt"] == 1
    assert events[0]["max_attempts"] == 3
    assert events[0]["retryable"] is True
    assert events[0]["error_type"] == "RuntimeError"


def test_retry_with_backoff_emits_exhausted_event():
    events: list[dict[str, object]] = []

    def always_fails() -> str:
        raise RuntimeError("temporary 500")

    try:
        retry_with_backoff(
            operation=always_fails,
            max_attempts=2,
            base_delay=0.1,
            max_delay=1.0,
            jitter_ratio=0.0,
            sleeper=lambda _: None,
            should_retry=lambda exc: "500" in str(exc),
            on_event=events.append,
        )
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError")

    assert [event["event"] for event in events] == [
        "guardrail.retry_scheduled",
        "guardrail.retry_exhausted",
    ]
    assert events[-1]["attempt"] == 2
    assert events[-1]["max_attempts"] == 2


def test_circuit_breaker_emits_open_block_and_close_events():
    events: list[dict[str, object]] = []
    now = {"value": 10.0}

    def fake_monotonic() -> float:
        return now["value"]

    breaker = CircuitBreaker(
        failure_threshold=2,
        reset_timeout=5.0,
        monotonic=fake_monotonic,
        on_event=events.append,
    )

    breaker.record_failure()
    breaker.record_failure()
    assert breaker.allow() is False
    breaker.record_success()

    assert [event["event"] for event in events] == [
        "guardrail.circuit_opened",
        "guardrail.circuit_blocked",
        "guardrail.circuit_closed_after_success",
    ]
    assert events[0]["consecutive_failures"] == 2
    assert events[0]["failure_threshold"] == 2
    assert events[1]["reset_timeout_sec"] == 5.0
    assert events[2]["previous_consecutive_failures"] == 2

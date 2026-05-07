from __future__ import annotations

from random import random
from time import monotonic, sleep
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class RateLimiter:
    def __init__(
        self,
        qps: float,
        monotonic: Callable[[], float] = monotonic,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        self.qps = qps
        self._monotonic = monotonic
        self._sleeper = sleeper
        self._last_called_at: float | None = None

    def wait(self) -> None:
        if self.qps <= 0:
            return

        now = self._monotonic()
        interval = 1.0 / self.qps
        if self._last_called_at is None:
            self._last_called_at = now
            return

        elapsed = now - self._last_called_at
        if elapsed < interval:
            self._sleeper(interval - elapsed)
            now = self._monotonic()

        self._last_called_at = now


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int,
        reset_timeout: float,
        monotonic: Callable[[], float] = monotonic,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self._monotonic = monotonic
        self._consecutive_failures = 0
        self._opened_at: float | None = None

    def allow(self) -> bool:
        if self._opened_at is None:
            return True

        now = self._monotonic()
        if now - self._opened_at >= self.reset_timeout:
            self._opened_at = None
            self._consecutive_failures = 0
            return True

        return False

    def record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.failure_threshold:
            self._opened_at = self._monotonic()

    def record_success(self) -> None:
        self._consecutive_failures = 0
        self._opened_at = None


class RequestCache(Generic[T]):
    def __init__(self) -> None:
        self._cache: dict[tuple[str, str], T] = {}

    def has(self, key: tuple[str, str]) -> bool:
        return key in self._cache

    def get(self, key: tuple[str, str]) -> T:
        return self._cache[key]

    def set(self, key: tuple[str, str], value: T) -> None:
        self._cache[key] = value


def retry_with_backoff(
    operation: Callable[[], T],
    max_attempts: int,
    base_delay: float,
    max_delay: float,
    jitter_ratio: float,
    sleeper: Callable[[float], None] = sleep,
) -> T:
    for attempt in range(1, max_attempts + 1):
        try:
            return operation()
        except Exception:
            if attempt >= max_attempts:
                raise
            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = delay * jitter_ratio * random()
            sleeper(delay + jitter)

    raise RuntimeError("unreachable")

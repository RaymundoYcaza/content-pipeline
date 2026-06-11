import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryError(RuntimeError):
    pass


def retry_with_backoff(
    func: Callable[[], T],
    max_retries: int,
    base_delay_seconds: float,
    retryable_statuses: tuple[int, ...] = (429, 500, 502, 503, 504),
) -> T:
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code not in retryable_statuses or attempt >= max_retries:
                last_error = exc
                break
            sleep_for = base_delay_seconds * (2 ** attempt) + random.uniform(0, 0.5)
            time.sleep(sleep_for)
            last_error = exc
    raise RetryError(str(last_error)) from last_error

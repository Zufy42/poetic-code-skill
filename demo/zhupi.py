"""铸坯：带限流、重试、降级的 HTTP 客户端组件（正常工程版）"""
import time


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: float, capacity: int = 10):
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last = time.monotonic()

    def acquire(self):
        while True:
            now = time.monotonic()
            self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= 1:
                self.tokens -= 1
                return
            time.sleep((1 - self.tokens) / self.rate)


class TransientError(Exception):
    pass


def request_with_retry(fetch, retries=5, base_delay=1):
    for attempt in range(retries):
        try:
            return fetch()
        except TransientError:
            if attempt == retries - 1:
                raise
            time.sleep(base_delay * 2 ** attempt)


class Client:
    def __init__(self, limiter: RateLimiter, retries: int = 5):
        self.limiter = limiter
        self.retries = retries
        self.cache = {}

    def get(self, name, primary, fallback=None):
        self.limiter.acquire()
        try:
            result = request_with_retry(primary, self.retries)
            self.cache[name] = result
            return result
        except TransientError:
            if fallback is not None:
                return fallback()
            if name in self.cache:
                return self.cache[name]
            raise

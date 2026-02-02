import time
import threading
from typing import Optional

class AdaptiveRateLimiter:
    """
    Thread-safe token bucket rate limiter with adaptive backoff.
    """
    
    def __init__(self, requests_per_second: float = 1.0):
        self.capacity = requests_per_second
        self.tokens = requests_per_second
        self.last_refill = time.time()
        self.lock = threading.Lock()
        self.backoff_factor = 1.0

    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * (self.capacity / self.backoff_factor))
        self.last_refill = now

    def wait(self):
        """Waits until a token is available."""
        while True:
            with self.lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
            time.sleep(0.1)

    def report_error_429(self):
        """Adopts a more conservative rate after a 429 Too Many Requests."""
        with self.lock:
            self.backoff_factor = min(32.0, self.backoff_factor * 2.0)
            self.tokens = 0  # Drain tokens immediately

    def report_success(self):
        """Slowly recovers to the base rate after successful requests."""
        with self.lock:
            self.backoff_factor = max(1.0, self.backoff_factor * 0.9)

if __name__ == "__main__":
    limiter = AdaptiveRateLimiter(5.0)
    for i in range(10):
        limiter.wait()
        print(f"Request {i} at {time.time()}")

import threading
import time


class RateLimiter:
    def __init__(self, rate):
        self.rate = rate
        self.last_called = time.time()
        self.mutex = threading.Lock()
        self.counter = 0

    def limit(self, func, *args, **kwargs):
        with self.mutex:
            now = time.time()
            elapsed_time = now - self.last_called
            if self.counter >= self.rate:
                if elapsed_time < 1:
                    sleep_time = 1 - elapsed_time
                    time.sleep(sleep_time)
                self.counter = 0
                self.last_called = time.time()
            self.counter += 1
            return func(*args, **kwargs)

from contextlib import contextmanager
from timeit import default_timer


class ElapsedTimer:
    def __init__(self):
        self.start = default_timer()

    def elapsed(self) -> int:
        return int((default_timer() - self.start) * 1000)

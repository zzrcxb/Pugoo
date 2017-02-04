from time import time

class Monitor:
    def __init__(self):
        self.start = time()
        self.tictoc = {}
        self.starts = {}

    def enter(self, key):
        self.starts[key] = time()

    def leave(self, key):
        period = time() - self.starts.get(key, time())
        if key in self.tictoc:
            self.tictoc[key] += period
        else:
            self.tictoc[key] = period

    def __str__(self):
        return repr(self.tictoc)
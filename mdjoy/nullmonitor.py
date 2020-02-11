# Copyright 2020 Olivier Fisette

class NullMonitor:

    def __init__(self, maxval=0):
        pass

    def start(self):
        return self

    def update(self, val):
        return self

    def finish(self):
        return self

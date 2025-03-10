import shelve

class CommandCache:
    def __init__(self, filename="command_cache.db"):
        self.filename = filename

    def get(self, key):
        with shelve.open(self.filename) as cache:
            return cache.get(key, None)

    def set(self, key, value):
        with shelve.open(self.filename) as cache:
            cache[key] = value

cache = CommandCache()

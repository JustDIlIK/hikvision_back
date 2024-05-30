class PersonCache:
    def __init__(self):
        self.cache = {}
        self.need_update = True

    def get(self):
        return self.cache

    def set(self, person_code, person):
        self.cache[person_code] = person


person_cache = PersonCache()

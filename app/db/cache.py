from datetime import datetime


class BaseCache:
    def __init__(self):
        self.cache = {}
        self.lt = datetime.now()
        self.need_update = True

    def get(self):
        return self.cache

    def set(self, index, value):
        self.cache[index] = value


class PersonCache(BaseCache):
    pass


class AttendanceCache(BaseCache):
    def __init__(self):
        super().__init__()
        self.date_status = {}


person_cache = PersonCache()
attendance_cache = AttendanceCache()

from datetime import datetime

from app.logs.logger import get_logger


class BaseCache:
    def __init__(self):
        self.cache = {}
        self.lt = datetime.now()
        self.need_update = True

    def get(self):
        return self.cache

    def set(self, index, value):
        self.cache[index] = value

    def clear(self, index):
        self.cache.pop(index)


class PersonCache(BaseCache):
    pass


class AttendanceCache(BaseCache):
    def __init__(self):
        super().__init__()
        self.status = {}
        self.left_time = {}

    def clear(self, index):
        super().clear(index)
        self.status.pop(index)


person_cache = PersonCache()
attendance_cache = AttendanceCache()

logger = get_logger(__name__)
logger.info("Кэширование запущено")

import redis
import json
from datetime import datetime


class DatetimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class RedisClient:
    def __init__(self, host='localhost', port=6379, username=None, password=None, db=0):
        self.redis = redis.Redis(host=host, port=port, username=username, password=password, db=db)

    def set(self, key, value, expire=None):
        self.redis.set(key, value, ex=expire)

    def get(self, key):
        return self.redis.get(key)

    def set_dict(self, key, value, expire=None):
        serialized_value = json.dumps(value, cls=DatetimeEncoder)
        self.redis.set(key, serialized_value, ex=expire)

    def get_dict(self, key):
        serialized_value = self.redis.get(key)
        if serialized_value is None:
            return None
        return json.loads(serialized_value)

    def delete(self, key):
        self.redis.delete(key)

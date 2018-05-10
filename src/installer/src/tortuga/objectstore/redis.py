from redis import Redis

from .base import ObjectStore


class RedisObjectStore(ObjectStore):
    """
    An implementation of the ObjectStore that stores objects in an Redis
    KV store.

    """
    def __init__(self, namespace: str, **kwargs):
        """
        Initialization.

        :param str namespace: the namespace to use for storing objects
        :param str kwargs:    passed to the redis client on initialization

        """
        super().__init__(namespace)
        self._redis = Redis(**kwargs)

    def set(self, key: str, value: dict):
        self._redis.hmset(self.get_key_name(key), value)

    def get(self, key: str) -> dict:
        return self._redis.hgetall(self.get_key_name(key))

    def delete(self, key: str):
        self._redis.delete(self.get_key_name(key))

    def exists(self, key: str) -> bool:
        return self._redis.exists(self.get_key_name(key))

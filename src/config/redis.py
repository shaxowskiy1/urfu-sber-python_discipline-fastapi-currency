import redis
from typing import Optional


class RedisClient:
   
    _instance: Optional['RedisClient'] = None
    _redis_client: Optional[redis.Redis] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._redis_client is None:
            try:
                self._redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                self._redis_client.ping()
            except redis.ConnectionError as e:
                raise RuntimeError(f"Ошибка подключения к Redis: {e}")
    
    @property
    def client(self) -> redis.Redis:
        if self._redis_client is None:
            raise RuntimeError("Redis клиент не инициализирован")
        return self._redis_client


def get_redis_client() -> redis.Redis:
    redis_instance = RedisClient()
    return redis_instance.client



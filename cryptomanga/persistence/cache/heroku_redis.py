import os
from datetime import timedelta
from urllib.parse import urlparse

import redis


class HerokuRedis:
    REDIS_TLS_URL = "REDIS_TLS_URL"
    COUNTER_TTL = timedelta(seconds=900)  # 15 minutes

    def __init__(self):
        url = urlparse(os.environ[HerokuRedis.REDIS_TLS_URL])
        self._r = redis.Redis(
            host=url.hostname,
            port=url.port,
            username=url.username,
            password=url.password,
            ssl=True,
            ssl_cert_reqs=None,
        )

    def incr(self, key: str) -> int:
        val = self._r.incr(key)
        self._r.expire(key, time=HerokuRedis.COUNTER_TTL)
        return val

    def incr_no_exp(self, key: str) -> int:
        val = self._r.incr(key)
        return val

    def set(self, key: str, value: str, time=timedelta(hours=24)) -> None:
        self._r.setex(name=key, value=value, time=time)

    def exists(self, key: str) -> bool:
        return self._r.exists(key)

    def get(self, key: str):
        return self._r.get(key)

    def delete(self, key: str) -> None:
        self._r.delete(key)

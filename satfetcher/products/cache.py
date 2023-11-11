import redis
import numpy as np
import json
import os
import io

_redis = redis.Redis(host=os.getenv('REDISHOST'),
                     port=int(os.getenv('REDISPORT')),
                     username=os.getenv('REDISUSER'),
                     password=os.getenv('REDISPASSWORD'),
                     decode_responses=False)

class Cache:
    def geoset(self, name, val, expire=None):
        _redis.geoadd(name, val)
        if expire:
            _redis.expire(name, time=expire)

    def geoget(self, name, lat, lon, radius=1):
        if _redis.exists(name) == 0:
            return None

        res = _redis.geosearch(name,
                               latitude=lat,
                               longitude=lon,
                               radius=radius,
                               unit='km',
                               withcoord=True,
                               withdist=True,
                               sort='ASC')
        return res

    def hset(self, name: str, val: dict, expire=None):
        _redis.hset(name, mapping=val)
        if expire:
            _redis.expire(name, time=expire)

    def hget(self, name: str):
        return _redis.hgetall(name)

    def set(self, name: str, val, expire=None):
        if not isinstance(val, str):
            val = json.dumps(val)
        _redis.set(name, val)

    def get(self, name: str, convert=False):
        res = _redis.get(name)
        if convert:
            res = json.loads(res)
        return res

    def npset(self, name: str, val: np.ndarray, expire=None):
        with io.BytesIO() as memfd:
            np.save(memfd, val, allow_pickle=False)
            memfd.seek(0)

            buf = memfd.getvalue()
            _redis.set(name, buf, ex=expire)

    def npget(self, name: str):
        res = _redis.get(name)
        if res is not None:
            with io.BytesIO(res) as memfd:
                arr = np.load(memfd)
            return arr

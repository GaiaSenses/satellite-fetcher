import redis
import os

_redis = redis.Redis(host=os.getenv('REDIS_HOST'),
                     port=int(os.getenv('REDIS_PORT')),
                     password=os.getenv('REDIS_PASSWORD'),
                     decode_responses=True)

class Cache:
    def geoset(self, name, lat, lon, val, expire=None):
        _redis.geoadd(name, [lon, lat, val])
        if expire:
            _redis.expire(name, time=expire)

    def geoget(self, name, lat, lon, radius=1):
        res = _redis.geosearch(name,
                               latitude=lat,
                               longitude=lon,
                               radius=radius,
                               unit='km',
                               withcoord=True,
                               withdist=True)
        return res

    def set(self, name: str, val: dict, expire=None):
        _redis.hset(name, mapping=val)
        if expire:
            _redis.expire(name, time=expire)

    def get(self, name: str):
        return _redis.hgetall(name)

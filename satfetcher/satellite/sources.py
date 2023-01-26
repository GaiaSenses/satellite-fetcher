import abc
import json
import os
from datetime import datetime, timedelta
from urllib.request import urlopen

import boto3
from botocore import UNSIGNED
from botocore.config import Config


class DataSource(abc.ABC):
    @abc.abstractmethod
    def get(self, *args, **kwargs):
        pass


class DataSourceFactory:
    def __init__(self) -> None:
        self._sources = {}

    def create(self, name):
        if name in self._sources:
            return self._sources[name]

        if name == 'lightning':
            src = GOESSource('GLM-L2-LCFA')
        elif name == 'rainfall':
            src = OWSource()
        elif name == 'fire':
            src = INPESource()
        else:
            raise ValueError(
                f"{name} must be one of ['lightning', 'fire', 'rain']")

        self._sources[name] = src
        return src


class GOESResponse:
    def __init__(self, key, date, body):
        self.key = key
        self.date = date
        self.body = body


class JSONResponse:
    def __init__(self, body):
        self.body = body


class GOESSource(DataSource):
    def __init__(self, product, maxcache=3):
        super().__init__()

        self._s3 = boto3.resource(
            's3', config=Config(signature_version=UNSIGNED))
        self._bucket = self._s3.Bucket('noaa-goes16')
        self._product = product

        self._cache = {}
        self._maxcache = maxcache

    def get(self, n=1, *args, **kwargs):
        latest = self._nlatest(n)
        res = []
        for resource in latest:
            if resource.key in self._cache:
                res.append(self._cache[resource.key])
            else:
                obj = resource.get()
                response = GOESResponse(
                    resource.key, resource.last_modified, obj['Body'].read())

                self._cache[response.key] = response
                if len(self._cache) > self._maxcache:
                    keys = sorted(self._cache.keys())
                    del self._cache[keys[0]]

                res.append(response)

        return res

    def _nlatest(self, n):
        res = []
        h = 0
        while len(res) < n:
            dt = datetime.utcnow() - timedelta(hours=h)
            prefix = self._prefix(dt)
            objects = list(self._bucket.objects.filter(Prefix=prefix))
            res += objects[(len(res) - n):]
        return res

    def _prefix(self, utc: datetime):
        year = utc.year
        day = utc.strftime('%j')
        hour = utc.hour
        return f'{self._product}/{year}/{day}/{hour}'


class INPESource(DataSource):
    API_URL = 'http://queimadas.dgi.inpe.br/api'
    COUNTRY = 33  # Brasil

    def __init__(self, cache_timeout=600):
        super().__init__()
        self._cache = None
        self._timeout = timedelta(seconds=cache_timeout)

    def get(self, *args, **kwargs):
        if self._cache:
            now = datetime.now()
            if now - self._cache['time'] < self._timeout:
                return self._cache['response']

        with urlopen(f'{self.API_URL}/focos?pais_id={self.COUNTRY}') as res:
            self._cache = {
                'time': datetime.now(),
                'response': JSONResponse(json.load(res))
            }
            return self._cache['response']


class OWSource(DataSource):
    API_URL = 'https://api.openweathermap.org/data/2.5/weather?appid={key}&lat={lat}&lon={lon}&units=metric'
    API_KEY = os.getenv('OPENWEATHER_API_KEY')

    def __init__(self):
        super().__init__()

    def get(self, lat, lon, *args, **kwargs):
        with urlopen(self.API_URL.format(key=self.API_KEY, lat=lat, lon=lon)) as res:
            return JSONResponse(json.load(res))
